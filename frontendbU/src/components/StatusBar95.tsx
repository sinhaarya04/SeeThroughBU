import { ReactNode } from "react";

interface StatusBar95Props {
  children: ReactNode;
}

export const StatusBar95 = ({ children }: StatusBar95Props) => {
  return (
    <div className="border-sunken bg-background p-1 mt-2 flex items-center gap-3 text-xs">
      {children}
    </div>
  );
};

interface LEDProps {
  label: string;
  on?: boolean;
}

export const LED = ({ label, on = false }: LEDProps) => {
  return (
    <div className="flex items-center gap-1.5 border-sunken px-2 py-0.5">
      <div className={`w-2 h-2 rounded-full ${on ? 'led-on' : 'led-off'}`} />
      <span>{label}</span>
    </div>
  );
};
