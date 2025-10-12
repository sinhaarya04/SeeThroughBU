import { ReactNode } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

interface Modal95Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export const Modal95 = ({ open, onOpenChange, title, description, children, className }: Modal95Props) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className={cn("border-window bg-background p-0 gap-0 max-w-2xl [&>button]:hidden", className)}>
        {/* Title Bar */}
        <DialogHeader className="bg-primary text-primary-foreground px-2 py-1 flex flex-row items-center justify-between space-y-0">
          <div className="flex items-center gap-2">
            <span className="text-sm">🪟</span>
            <DialogTitle className="pixel-text text-[10px] text-primary-foreground">{title}</DialogTitle>
          </div>
          <button 
            onClick={() => onOpenChange(false)}
            className="border-raised bg-background hover:bg-destructive hover:text-destructive-foreground w-5 h-5 flex items-center justify-center text-[10px] font-bold text-foreground"
          >
            ×
          </button>
        </DialogHeader>
        
        <div className="p-4">
          {description && (
            <DialogDescription className="mb-4 text-sm">{description}</DialogDescription>
          )}
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
};
