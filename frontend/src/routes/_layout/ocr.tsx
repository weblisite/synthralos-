import { createFileRoute } from "@tanstack/react-router"
import { OCRJobManager } from "@/components/OCR/OCRJobManager"

export const Route = createFileRoute("/_layout/ocr")({
  component: OCRPage,
  head: () => ({
    meta: [
      {
        title: "OCR - SynthralOS",
      },
    ],
  }),
})

function OCRPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">OCR Management</h1>
        <p className="text-muted-foreground mt-2">
          Extract text from documents using multiple OCR engines
        </p>
      </div>
      <OCRJobManager />
    </div>
  )
}
