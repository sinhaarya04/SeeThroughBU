import { cn } from "@/lib/utils";

interface Badge95Props {
  children: React.ReactNode;
  variant?: "default" | "danger" | "success" | "warning";
  icon?: string;
  className?: string;
}

export const Badge95 = ({ children, variant = "default", icon, className }: Badge95Props) => {
  const variantClasses = {
    default: "bg-muted text-muted-foreground",
    danger: "bg-destructive text-destructive-foreground",
    success: "bg-success text-success-foreground",
    warning: "bg-accent text-accent-foreground",
  };

  return (
    <div className={cn(
      "border-raised inline-flex items-center gap-1.5 px-2 py-1 text-xs font-bold uppercase",
      variantClasses[variant],
      className
    )}>
      {icon && <span>{icon}</span>}
      <span>{children}</span>
    </div>
  );
};
