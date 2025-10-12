import { ReactNode, ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface Button95Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  icon?: string;
  variant?: "default" | "primary" | "danger" | "success";
}

export const Button95 = ({ 
  children, 
  icon, 
  variant = "default", 
  className,
  disabled,
  ...props 
}: Button95Props) => {
  const variantClasses = {
    default: "bg-background hover:bg-muted",
    primary: "bg-primary text-primary-foreground hover:brightness-110",
    danger: "bg-destructive text-destructive-foreground hover:brightness-110",
    success: "bg-success text-success-foreground hover:brightness-110",
  };

  return (
    <button
      className={cn(
        "border-raised px-4 py-2 flex items-center justify-center gap-2 text-sm transition-all",
        "active:border-sunken active:translate-y-[1px]",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:active:translate-y-0",
        variantClasses[variant],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {icon && <span>{icon}</span>}
      <span>{children}</span>
    </button>
  );
};
