import { ReactNode, useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Window95Props {
  title?: string;
  icon?: string;
  children: ReactNode;
  className?: string;
  onExportData?: () => void;
  onClearData?: () => void;
  onShowAbout?: () => void;
  onShowHelp?: () => void;
  onShowContact?: () => void;
  onShowPreferences?: () => void;
  onShowFeatureRequest?: () => void;
}

export const Window95 = ({ 
  title = "See-Through Checkout v1.0", 
  icon = "🖥️", 
  children, 
  className = "",
  onExportData,
  onClearData,
  onShowAbout,
  onShowHelp,
  onShowContact,
  onShowPreferences,
  onShowFeatureRequest,
}: Window95Props) => {
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  return (
    <div className={`border-window bg-background ${className}`}>
      {/* Title Bar */}
      <div className="bg-primary text-primary-foreground px-1 py-1 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm">{icon}</span>
          <span className="pixel-text text-[10px]">{title}</span>
        </div>
        <div className="flex gap-1">
          <button className="border-raised bg-background hover:bg-muted w-5 h-5 flex items-center justify-center text-[10px] font-bold">
            _
          </button>
          <button className="border-raised bg-background hover:bg-muted w-5 h-5 flex items-center justify-center text-[10px] font-bold">
            □
          </button>
          <button className="border-raised bg-background hover:bg-destructive hover:text-destructive-foreground w-5 h-5 flex items-center justify-center text-[10px] font-bold">
            ×
          </button>
        </div>
      </div>
      
      {/* Menu Bar */}
      <div className="border-b border-border bg-background px-1 py-0.5">
        <div className="flex gap-4 text-sm">
          {/* File Menu */}
          <DropdownMenu open={openMenu === 'file'} onOpenChange={(open) => setOpenMenu(open ? 'file' : null)}>
            <DropdownMenuTrigger asChild>
              <button className="hover:bg-primary hover:text-primary-foreground px-2 py-0.5">
                File
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48 border-window bg-background">
              <DropdownMenuItem onClick={onExportData} className="text-xs">
                📄 Export Scan Data
              </DropdownMenuItem>
              <DropdownMenuItem className="text-xs">
                💾 Save Evidence
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onClearData} className="text-xs">
                🗑️ Clear All Data
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-xs text-muted-foreground">
                ❌ Exit
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Edit Menu */}
          <DropdownMenu open={openMenu === 'edit'} onOpenChange={(open) => setOpenMenu(open ? 'edit' : null)}>
            <DropdownMenuTrigger asChild>
              <button className="hover:bg-primary hover:text-primary-foreground px-2 py-0.5">
                Edit
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48 border-window bg-background">
              <DropdownMenuItem onClick={onShowPreferences} className="text-xs">
                ⚙️ Preferences
              </DropdownMenuItem>
              <DropdownMenuItem className="text-xs">
                🔔 Notification Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-xs">
                📊 Detection Sensitivity
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Help Menu */}
          <DropdownMenu open={openMenu === 'help'} onOpenChange={(open) => setOpenMenu(open ? 'help' : null)}>
            <DropdownMenuTrigger asChild>
              <button className="hover:bg-primary hover:text-primary-foreground px-2 py-0.5">
                Help
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-48 border-window bg-background">
              <DropdownMenuItem onClick={onShowHelp} className="text-xs">
                📖 User Guide
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onShowContact} className="text-xs">
                📞 Contact Support
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-xs">
                🐛 Report Bug
              </DropdownMenuItem>
              <DropdownMenuItem onClick={onShowFeatureRequest} className="text-xs">
                💡 Request Feature
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={onShowAbout} className="text-xs">
                ℹ️ About See-Through
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Content */}
      <div className="p-2">
        {children}
      </div>
    </div>
  );
};
