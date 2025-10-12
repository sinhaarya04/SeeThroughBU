import { ReactNode } from "react";

interface Card95Props {
  title?: string;
  children: ReactNode;
  className?: string;
}

export const Card95 = ({ title, children, className = "" }: Card95Props) => {
  return (
    <div className={`border-raised bg-card p-3 ${className}`}>
      {title && (
        <div className="mb-3 pb-2 border-b border-border">
          <h3 className="pixel-text text-[10px] text-foreground">{title}</h3>
        </div>
      )}
      <div className="text-card-foreground">
        {children}
      </div>
    </div>
  );
};
