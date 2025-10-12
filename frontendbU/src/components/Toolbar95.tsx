import { ReactNode } from "react";

interface Toolbar95Props {
  children: ReactNode;
}

export const Toolbar95 = ({ children }: Toolbar95Props) => {
  return (
    <div className="border-raised bg-background p-1 flex gap-1 mb-2">
      {children}
    </div>
  );
};
