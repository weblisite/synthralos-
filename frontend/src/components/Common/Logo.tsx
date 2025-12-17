import { Link } from "@tanstack/react-router"

import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const content =
    variant === "responsive" ? (
      <>
        <span
          className={cn(
            "text-xl font-bold bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 bg-clip-text text-transparent group-data-[collapsible=icon]:hidden",
            className,
          )}
        >
          SynthralOS
        </span>
        <span
          className={cn(
            "text-lg font-bold bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 bg-clip-text text-transparent hidden group-data-[collapsible=icon]:block",
            className,
          )}
        >
          S
        </span>
      </>
    ) : variant === "full" ? (
      <span
        className={cn(
          "text-xl font-bold bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 bg-clip-text text-transparent",
          className,
        )}
      >
        SynthralOS
      </span>
    ) : (
      <span
        className={cn(
          "text-lg font-bold bg-gradient-to-r from-orange-500 via-pink-500 to-purple-600 bg-clip-text text-transparent",
          className,
        )}
      >
        S
      </span>
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
