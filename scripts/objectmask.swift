// قصّ «شي» من كل فريم ويتبعه (Vision — ماك 14+) — للإضاءة الانتقائية (29_spotlight.py)
// objectmask <inDir> <outDir> <x> <y> [feather]
//   x,y = نقطة على الشي بأول فريم (نسبة 0…1 من عرض/طول الكادر، أصلها أعلى يسار)
//   كل فريم: يختار الجزء (instance) اللي تحت النقطة، ثم النقطة تمشي لمركزه — فيتبعه لو تحرّك.
// ⛔ Vision يشوف «الشخص + اللي بيده» جزءاً واحداً غالباً — الأفضل للأشياء المنفصلة (على طاولة، رف، جدار).
import Foundation
import Vision
import CoreImage

let a = CommandLine.arguments
guard a.count >= 5, var px = Double(a[3]), var py = Double(a[4]) else {
    print("usage: objectmask <inDir> <outDir> <x> <y> [feather]"); exit(2) }
let inDir = a[1], outDir = a[2]
let feather = a.count > 5 ? Double(a[5]) ?? 2.0 : 2.0
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)
let ctx = CIContext()
let files = (try FileManager.default.contentsOfDirectory(atPath: inDir)).filter { $0.hasSuffix(".jpg") }.sorted()
var found = 0, lost = 0
var lastMask: CIImage? = nil

for f in files {
    guard let img = CIImage(contentsOf: URL(fileURLWithPath: inDir + "/" + f)) else { continue }
    let W = img.extent.width, H = img.extent.height
    let out = URL(fileURLWithPath: outDir + "/" + f.replacingOccurrences(of: ".jpg", with: ".png"))
    let h = VNImageRequestHandler(ciImage: img, options: [:])
    let req = VNGenerateForegroundInstanceMaskRequest()
    var mask: CIImage? = nil
    if (try? h.perform([req])) != nil, let r = req.results?.first {
        // خريطة الأجزاء: كل بكسل رقم الجزء (0 = خلفية)
        let lab = r.instanceMask
        CVPixelBufferLockBaseAddress(lab, .readOnly)
        let lw = CVPixelBufferGetWidth(lab), lh = CVPixelBufferGetHeight(lab), rb = CVPixelBufferGetBytesPerRow(lab)
        let base = CVPixelBufferGetBaseAddress(lab)!.assumingMemoryBound(to: UInt8.self)
        let cx = min(lw - 1, max(0, Int(px * Double(lw)))), cy = min(lh - 1, max(0, Int(py * Double(lh))))
        var id = Int(base[cy * rb + cx])
        if id == 0 {                                   // النقطة طاحت على حافة — دوّر حولها
            let R = max(lw, lh) / 30
            search: for d in stride(from: 1, through: R, by: 1) {
                for (dx, dy) in [(d,0),(-d,0),(0,d),(0,-d),(d,d),(-d,-d),(d,-d),(-d,d)] {
                    let x = cx + dx, y = cy + dy
                    if x >= 0 && y >= 0 && x < lw && y < lh && base[y * rb + x] != 0 { id = Int(base[y * rb + x]); break search }
                }
            }
        }
        if id != 0 {                                   // مركز الجزء = النقطة للفريم الجاي
            var sx = 0, sy = 0, n = 0
            for y in 0..<lh { for x in 0..<lw where Int(base[y * rb + x]) == id { sx += x; sy += y; n += 1 } }
            if n > 0 { px = Double(sx) / Double(n) / Double(lw); py = Double(sy) / Double(n) / Double(lh) }
        }
        CVPixelBufferUnlockBaseAddress(lab, .readOnly)
        if id != 0, let buf = try? r.generateScaledMaskForImage(forInstances: IndexSet(integer: id), from: h) {
            var m = CIImage(cvPixelBuffer: buf)
            m = m.transformed(by: CGAffineTransform(scaleX: W / m.extent.width, y: H / m.extent.height))
            mask = m
        }
    }
    if mask == nil { lost += 1; mask = lastMask } else { found += 1; lastMask = mask }   // فريم ضايع؟ خذ اللي قبله
    guard var m = mask else {
        let empty = CIImage(color: .black).cropped(to: CGRect(x: 0, y: 0, width: W, height: H))
        try? ctx.writePNGRepresentation(of: empty, to: out, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray()); continue }
    if feather > 0 {
        m = m.clampedToExtent().applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: feather])
             .cropped(to: CGRect(x: 0, y: 0, width: W, height: H))
    }
    try? ctx.writePNGRepresentation(of: m, to: out, format: .L8, colorSpace: CGColorSpaceCreateDeviceGray())
}
print("object: \(found) found · \(lost) lost of \(files.count)")
exit(found == 0 ? 3 : 0)
