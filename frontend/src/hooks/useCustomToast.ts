import { useCallback } from "react"
import { toast } from "sonner"

const useCustomToast = () => {
  const showSuccessToast = useCallback(
    (description: string, title?: string) => {
      toast.success(title || "Success!", {
        description,
        duration: 5000, // Show for 5 seconds
      })
    },
    [],
  )

  const showErrorToast = useCallback((description: string, title?: string) => {
    toast.error(title || "Something went wrong!", {
      description,
      duration: 5000, // Show for 5 seconds
    })
  }, [])

  return { showSuccessToast, showErrorToast }
}

export default useCustomToast
