import Foundation
import PDFKit
import Vision
import AppKit

// 사용법: ocr_pdf <pdf_path> <out_dir> [start_page_1based] [end_page_1based]
let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: \(args[0]) <pdf_path> <out_dir> [start_page] [end_page]\n", stderr)
    exit(1)
}

let pdfPath = args[1]
let outDir = args[2]
let pdfURL = URL(fileURLWithPath: pdfPath)

guard let doc = PDFDocument(url: pdfURL) else {
    fputs("Failed to open PDF: \(pdfPath)\n", stderr)
    exit(1)
}

let totalPages = doc.pageCount
let startPage = args.count >= 4 ? max(1, Int(args[3]) ?? 1) : 1
let endPage = args.count >= 5 ? min(totalPages, Int(args[4]) ?? totalPages) : totalPages

try FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

print("PDF: \(pdfPath) (total: \(totalPages) pages, processing: \(startPage)...\(endPage))")
fflush(stdout)

func renderPageToCGImage(_ page: PDFPage, scale: CGFloat = 2.0) -> CGImage? {
    let rect = page.bounds(for: .mediaBox)
    let width = Int(rect.width * scale)
    let height = Int(rect.height * scale)
    guard width > 0, height > 0 else { return nil }

    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let ctx = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return nil }

    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: width, height: height))
    ctx.saveGState()
    ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    ctx.restoreGState()
    return ctx.makeImage()
}

func ocrPage(_ cgImage: CGImage) -> String {
    var resultLines: [(y: CGFloat, x: CGFloat, text: String)] = []
    let request = VNRecognizeTextRequest { req, _ in
        guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
        for obs in observations {
            if let top = obs.topCandidates(1).first {
                let box = obs.boundingBox
                // Vision boundingBox origin is bottom-left (0..1)
                resultLines.append((y: box.midY, x: box.minX, text: top.string))
            }
        }
    }
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["ko-KR", "en-US"]
    request.usesLanguageCorrection = false // 코드 기호 왜곡 방지

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try? handler.perform([request])

    // 위에서 아래로(y 내림차순), 같은 줄(y 차이가 0.008 이내)이면 왼쪽에서 오른쪽으로(x 오름차순) 정렬
    resultLines.sort { a, b in
        if abs(a.y - b.y) > 0.008 {
            return a.y > b.y
        }
        return a.x < b.x
    }

    var mergedLines: [String] = []
    var currentY: CGFloat? = nil
    var currentRow: [String] = []

    for item in resultLines {
        if let cy = currentY, abs(cy - item.y) <= 0.008 {
            currentRow.append(item.text)
        } else {
            if !currentRow.isEmpty {
                mergedLines.append(currentRow.joined(separator: "    "))
            }
            currentY = item.y
            currentRow = [item.text]
        }
    }
    if !currentRow.isEmpty {
        mergedLines.append(currentRow.joined(separator: "    "))
    }

    return mergedLines.joined(separator: "\n")
}

let pageIndices = Array(startPage...endPage)
let lock = NSLock()
var completed = 0

// 병렬 처리 (동시 8워커로 고속 처리)
let semaphore = DispatchSemaphore(value: 8)
let group = DispatchGroup()
let queue = DispatchQueue(label: "ocr.worker", attributes: .concurrent)

for pageNum in pageIndices {
    let outFile = String(format: "%@/page_%04d.txt", outDir, pageNum)
    if FileManager.default.fileExists(atPath: outFile) {
        lock.lock()
        completed += 1
        lock.unlock()
        continue
    }

    semaphore.wait()
    group.enter()
    queue.async {
        defer {
            semaphore.signal()
            group.leave()
        }
        autoreleasepool {
            lock.lock()
            let pageObj = doc.page(at: pageNum - 1)
            lock.unlock()

            guard let page = pageObj, let cgImg = renderPageToCGImage(page, scale: 2.0) else {
                return
            }
            let text = ocrPage(cgImg)
            let header = "=== PAGE \(pageNum) ===\n"
            try? (header + text + "\n").write(toFile: outFile, atomically: true, encoding: .utf8)

            lock.lock()
            completed += 1
            if completed % 20 == 0 || completed == pageIndices.count {
                print("Progress: \(completed)/\(pageIndices.count) pages (\(outDir))")
                fflush(stdout)
            }
            lock.unlock()
        }
    }
}

group.wait()
print("Done! \(completed)/\(pageIndices.count) pages saved to \(outDir)")
