import { useCallback } from "react"
import { toast } from "sonner"

const useCustomToast = () => {
  const showSuccessToast = useCallback((description: string) => {
    toast.success("Success!", {
      description,
    })
  }, [])

  const showErrorToast = useCallback((description: string) => {
    toast.error("Something went wrong!", {
      description,
    })
  }, [])

  return { showSuccessToast, showErrorToast }
}

export default useCustomToast
