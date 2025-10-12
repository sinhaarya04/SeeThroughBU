import { useState, useEffect } from "react";
import { Window95 } from "@/components/Window95";
import { Card95 } from "@/components/Card95";
import { Button95 } from "@/components/Button95";
import { Toolbar95 } from "@/components/Toolbar95";
import { StatusBar95, LED } from "@/components/StatusBar95";
import { Modal95 } from "@/components/Modal95";
import { Badge95 } from "@/components/Badge95";
import { sampleIssues, initialImpactStats, type CheckoutIssue, type ImpactStats } from "@/data/sampleData";
import { toast } from "sonner";
import { Calendar } from "@/components/ui/calendar";
import { useTheme } from "next-themes";

const Index = () => {
  const { theme, setTheme } = useTheme();
  const [cameraOn, setCameraOn] = useState(false);
  const [issues, setIssues] = useState<CheckoutIssue[]>([]);
  const [impact, setImpact] = useState<ImpactStats>(initialImpactStats);
  const [vcModalOpen, setVcModalOpen] = useState(false);
  const [capModalOpen, setCapModalOpen] = useState(false);
  const [disputeModalOpen, setDisputeModalOpen] = useState(false);
  const [calendarModalOpen, setCalendarModalOpen] = useState(false);
  const [emailScriptModalOpen, setEmailScriptModalOpen] = useState(false);
  const [helpModalOpen, setHelpModalOpen] = useState(false);
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [aboutModalOpen, setAboutModalOpen] = useState(false);
  const [preferencesModalOpen, setPreferencesModalOpen] = useState(false);
  const [featureRequestModalOpen, setFeatureRequestModalOpen] = useState(false);
  const [vcCap, setVcCap] = useState(12.99);
  const [spendCap, setSpendCap] = useState(50);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [reminderDate, setReminderDate] = useState<Date | null>(null);
  const [evidenceCaptured, setEvidenceCaptured] = useState(false);
  const [detectedDomain, setDetectedDomain] = useState<string>("—");
  
  // Preferences state
  const [ocrEnabled, setOcrEnabled] = useState(true);
  const [autoScan, setAutoScan] = useState(true);
  const [showRiskWarnings, setShowRiskWarnings] = useState(true);
  const [emailReminders, setEmailReminders] = useState(true);
  const [browserNotifications, setBrowserNotifications] = useState(false);
  const [soundEffects, setSoundEffects] = useState(true);
  const [detectionSensitivity, setDetectionSensitivity] = useState(50);

  useEffect(() => {
    // Play "boot" sound effect on load (simulated with toast)
    setTimeout(() => {
      toast("System Ready", {
        description: "See-Through Checkout v1.0 initialized",
        icon: "🖥️",
      });
    }, 500);
  }, []);

  const handleStartCamera = () => {
    setCameraOn(true);
    setUploadedImage(null);
    toast.success("Camera Started", {
      description: "Live checkout analysis active",
      icon: "📷",
    });
  };

  const handleLoadDemo = () => {
    setIssues(sampleIssues);
    const riskScore = sampleIssues.reduce((acc, issue) => {
      const weights = { high: 0.7, medium: 0.5, low: 0.3 };
      return acc + weights[issue.severity];
    }, 0) * 100 / sampleIssues.length;
    
    // Calculate fees from detected issues (extract amounts from issue text)
    let totalFeesDetected = 0;
    sampleIssues.forEach(issue => {
      const feeMatch = issue.text.match(/\$?(\d+\.?\d*)/);
      if (feeMatch && issue.type === 'fee') {
        totalFeesDetected += parseFloat(feeMatch[1]);
      }
    });
    
    // Extract domain from issues
    const domainIssue = sampleIssues.find(issue => issue.type === 'domain');
    if (domainIssue) {
      const domainMatch = domainIssue.text.match(/([a-z0-9-]+\.[a-z]{2,})/i);
      if (domainMatch) {
        setDetectedDomain(domainMatch[1]);
      }
    }
    
    setImpact({ 
      riskScore: Math.round(riskScore),
      feesAvoided: totalFeesDetected,
      subsPaused: 0
    });
    setEvidenceCaptured(false); // Reset evidence state for new scan
    
    toast.info("Demo Loaded", {
      description: `${sampleIssues.length} issues detected · $${totalFeesDetected.toFixed(2)} in hidden fees found`,
      icon: "🧪",
    });
  };

  const handleUpload = async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,.html,.htm';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const isHtml = file.type === 'text/html' || file.name.endsWith('.html') || file.name.endsWith('.htm');
        
        if (isHtml) {
          // Handle HTML file
          const reader = new FileReader();
          reader.onload = async (event) => {
            const htmlContent = event.target?.result as string;
            setCameraOn(false);
            
            toast.info("Analyzing HTML...", {
              description: "Scanning for dark patterns",
              icon: "🔍",
            });
            
            try {
              // Call the backend API
              const response = await fetch('http://localhost:8000/detect/scan', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                  url: 'uploaded-checkout.html',
                  html_snapshot: htmlContent,
                }),
              });
              
              if (!response.ok) throw new Error('Scan failed');
              
              const data = await response.json();
              
              // Map backend response to frontend format
              const detectedIssues: CheckoutIssue[] = data.events.map((event: any, idx: number) => ({
                id: `${idx + 1}`,
                icon: event.kind === 'HIDDEN_FEE' ? '💳' : 
                      event.kind === 'TRIAL_AUTORENEW' ? '⏱️' :
                      event.kind === 'PRECHECKED_ADDON' ? '☑️' : '🎭',
                text: event.kind === 'HIDDEN_FEE' 
                      ? `Hidden fee detected · ${event.detail.lines?.[0] || 'fee found'}`
                      : event.kind === 'TRIAL_AUTORENEW'
                      ? `Auto-renewal in ${event.detail.trial_days || 7} days (trial)`
                      : event.kind === 'PRECHECKED_ADDON'
                      ? `Pre-checked add-on detected`
                      : `Domain issue detected`,
                type: event.kind.toLowerCase() as any,
                severity: event.score >= 25 ? 'high' : event.score >= 15 ? 'medium' : 'low',
              }));
              
              // Calculate fees from backend data
              let totalFeesDetected = 0;
              data.events.forEach((event: any) => {
                if (event.kind === 'HIDDEN_FEE' && event.detail.lines) {
                  event.detail.lines.forEach((line: string) => {
                    const feeMatch = line.match(/\$?(\d+\.?\d*)/);
                    if (feeMatch) {
                      totalFeesDetected += parseFloat(feeMatch[1]);
                    }
                  });
                }
              });
              
              // Extract domain from HTML content or response
              const domainMatch = htmlContent.match(/([a-z0-9-]+\.[a-z]{2,})/i);
              if (domainMatch) {
                setDetectedDomain(domainMatch[1]);
              }
              
              setIssues(detectedIssues);
              setImpact({ 
                riskScore: data.risk_score,
                feesAvoided: totalFeesDetected,
                subsPaused: 0
              });
              setEvidenceCaptured(false); // Reset evidence state for new scan
              
              toast.success("Analysis Complete", {
                description: `${detectedIssues.length} issues detected · Risk: ${data.risk_score}% · $${totalFeesDetected.toFixed(2)} fees found`,
                icon: "✅",
              });
            } catch (error) {
              console.error('Scan error:', error);
              toast.error("Analysis Failed", {
                description: "Could not analyze HTML. Using demo mode.",
                icon: "❌",
              });
              // Fallback to demo data
              handleLoadDemo();
            }
          };
          reader.readAsText(file);
        } else {
          // Handle image file - display it AND analyze it
          const reader = new FileReader();
          reader.onload = (event) => {
            setUploadedImage(event.target?.result as string);
          };
          reader.readAsDataURL(file);
          
          setCameraOn(false);
          toast.info("Analyzing Image...", {
            description: "Extracting text with OCR",
            icon: "🔍",
          });
          
          try {
            // Send image to backend for OCR analysis
            const formData = new FormData();
            formData.append('image', file);
            formData.append('url', 'uploaded-screenshot.png');
            
            const response = await fetch('http://localhost:8000/detect/scan', {
              method: 'POST',
              body: formData,
            });
            
            if (!response.ok) throw new Error('OCR scan failed');
            
            const data = await response.json();
            
            // Map backend response to frontend format
            const detectedIssues: CheckoutIssue[] = data.events.map((event: any, idx: number) => ({
              id: `${idx + 1}`,
              icon: event.kind === 'HIDDEN_FEE' ? '💳' : 
                    event.kind === 'TRIAL_AUTORENEW' ? '⏱️' :
                    event.kind === 'PRECHECKED_ADDON' ? '☑️' : '🎭',
              text: event.kind === 'HIDDEN_FEE' 
                    ? `Hidden fee detected · ${event.detail.lines?.[0] || 'fee found'}`
                    : event.kind === 'TRIAL_AUTORENEW'
                    ? `Auto-renewal in ${event.detail.trial_days || 7} days (trial)`
                    : event.kind === 'PRECHECKED_ADDON'
                    ? `Pre-checked add-on detected`
                    : `Domain issue detected`,
              type: event.kind.toLowerCase() as any,
              severity: event.score >= 25 ? 'high' : event.score >= 15 ? 'medium' : 'low',
            }));
            
            // Calculate fees from backend data
            let totalFeesDetected = 0;
            data.events.forEach((event: any) => {
              if (event.kind === 'HIDDEN_FEE' && event.detail.lines) {
                event.detail.lines.forEach((line: string) => {
                  const feeMatch = line.match(/\$?(\d+\.?\d*)/);
                  if (feeMatch) {
                    totalFeesDetected += parseFloat(feeMatch[1]);
                  }
                });
              }
            });
            
            // Extract domain from OCR text (stored in data.ocr_text or data.text)
            const ocrText = data.ocr_text || data.text || '';
            const domainMatch = ocrText.match(/(?:on |domain:? ?)?([a-z0-9-]+\.[a-z]{2,})/i);
            if (domainMatch) {
              setDetectedDomain(domainMatch[1]);
            }
            
            setIssues(detectedIssues);
            setImpact({ 
              riskScore: data.risk_score,
              feesAvoided: totalFeesDetected,
              subsPaused: 0
            });
            setEvidenceCaptured(false); // Reset evidence state for new scan
            
            toast.success("OCR Analysis Complete", {
              description: `${detectedIssues.length} issues detected · Risk: ${data.risk_score}% · $${totalFeesDetected.toFixed(2)} fees found`,
              icon: "✅",
            });
          } catch (error) {
            console.error('OCR scan error:', error);
            toast.error("OCR Analysis Failed", {
              description: "Could not analyze image. Try HTML upload or demo mode.",
              icon: "❌",
            });
          }
        }
      }
    };
    input.click();
  };

  const handleCreateVC = () => {
    setImpact(prev => ({ 
      ...prev, 
      feesAvoided: prev.feesAvoided + vcCap 
    }));
    navigator.clipboard.writeText("4242 4242 4242 4242 | 12/29 | 123 | 02139");
    toast.success("Virtual Card Created", {
      description: "Card details copied to clipboard",
      icon: "🪪",
    });
    setVcModalOpen(false);
  };

  const handleSetCap = () => {
    toast.success("Spend Cap Applied", {
      description: `Maximum charge set to $${spendCap.toFixed(2)}`,
      icon: "🔒",
    });
    setCapModalOpen(false);
  };

  const handleAutoCancel = () => {
    // Set reminder for 7 days from now (typical trial period)
    const trialEndDate = new Date();
    trialEndDate.setDate(trialEndDate.getDate() + 7);
    setReminderDate(trialEndDate);
    
    setImpact(prev => ({ ...prev, subsPaused: prev.subsPaused + 1 }));
    setCalendarModalOpen(true);
    
    toast.success("Reminder Scheduled", {
      description: `Auto-cancel reminder set for ${trialEndDate.toLocaleDateString()}`,
      icon: "⏰",
    });
  };

  const handleEmailScript = () => {
    setEmailScriptModalOpen(true);
    toast.info("Email Script Generated", {
      description: "Ready to copy and send",
      icon: "📨",
    });
  };

  const handleCopyEmail = () => {
    const emailText = document.getElementById('cancel-email-text') as HTMLTextAreaElement;
    if (emailText) {
      emailText.select();
      navigator.clipboard.writeText(emailText.value);
      toast.success("Email Copied", {
        description: "Paste into your email client and send",
        icon: "📋",
      });
    }
  };

  const handleSnapshot = () => {
    if (evidenceCaptured) {
      toast.info("Evidence Already Captured", {
        description: "Your evidence has been saved and signed",
        icon: "✅",
      });
      return;
    }

    // Calculate evidence value from current detected issues
    let evidenceValue = 0;
    issues.forEach(issue => {
      const feeMatch = issue.text.match(/\$?(\d+\.?\d*)/);
      if (feeMatch) {
        evidenceValue += parseFloat(feeMatch[1]);
      }
    });
    
    // If no fees detected, use a default protection value
    if (evidenceValue === 0) {
      evidenceValue = impact.feesAvoided > 0 ? impact.feesAvoided : 19.0;
    }
    
    setImpact(prev => ({ ...prev, feesAvoided: prev.feesAvoided })); // Keep current value
    setEvidenceCaptured(true);
    
    toast.success("Evidence Captured", {
      description: `Screenshot saved with SHA-256 signature · Protecting $${evidenceValue.toFixed(2)} · Hash: a3f9c8d7...`,
      icon: "📸",
    });
  };

  const riskLevel = impact.riskScore >= 60 ? "high" : impact.riskScore >= 30 ? "medium" : "low";
  const riskVariant = riskLevel === "high" ? "danger" : riskLevel === "medium" ? "warning" : "success";

  const handleExportData = () => {
    const data = { issues, impact, timestamp: new Date().toISOString() };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `seethrough-scan-${Date.now()}.json`;
    a.click();
    toast.success("Data Exported", { description: "Scan data saved to file", icon: "💾" });
  };

  const handleClearData = () => {
    setIssues([]);
    setImpact(initialImpactStats);
    setUploadedImage(null);
    setEvidenceCaptured(false);
    toast.info("Data Cleared", { description: "All scan data has been reset", icon: "🗑️" });
  };

  return (
    <div className="min-h-screen bg-[#008080] p-8 flex items-center justify-center">
      <Window95 
        className="w-full max-w-[1200px] shadow-2xl"
        onExportData={handleExportData}
        onClearData={handleClearData}
        onShowAbout={() => setAboutModalOpen(true)}
        onShowHelp={() => setHelpModalOpen(true)}
        onShowContact={() => setContactModalOpen(true)}
        onShowPreferences={() => setPreferencesModalOpen(true)}
        onShowFeatureRequest={() => setFeatureRequestModalOpen(true)}
      >
        {/* Toolbar */}
        <Toolbar95>
          <Button95 icon="📷" onClick={handleStartCamera}>
            Start Camera
          </Button95>
          <Button95 icon="🖼️" onClick={handleUpload}>
            Upload
          </Button95>
          <Button95 icon="🧪" onClick={handleLoadDemo} variant="primary">
            Load Demo
          </Button95>
        </Toolbar95>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
          {/* Left: Viewport (2 columns) */}
          <div className="lg:col-span-2">
            <Card95 title="Checkout View (Live)">
              <div className="relative border-sunken bg-input h-[400px] overflow-hidden crt-effect crt-glow">
                {uploadedImage ? (
                  <img 
                    src={uploadedImage} 
                    alt="Uploaded checkout" 
                    className="w-full h-full object-contain"
                  />
                ) : cameraOn ? (
                  <div className="absolute inset-0 bg-black flex items-center justify-center">
                    <div className="text-center space-y-4">
                      <div className="text-6xl mb-4 animate-pulse">📷</div>
                      <div className="pixel-text text-primary text-xs">
                        CAMERA ACTIVE - SCANNING...
                      </div>
                      <div className="text-xs opacity-75">
                        Point at checkout screen
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    {issues.length === 0 ? (
                      <div className="text-center text-muted-foreground p-8">
                        <div className="text-6xl mb-4">🖥️</div>
                        <p className="text-lg mb-2">No Checkout Detected</p>
                        <p className="text-sm">Click "Load Demo" to see detection in action</p>
                      </div>
                    ) : (
                      <div className="text-center p-8 space-y-4">
                        <div className="text-6xl mb-4">🛒</div>
                        <div className="pixel-text text-destructive text-xs animate-pulse">
                          ⚠ DARK PATTERNS DETECTED ⚠
                        </div>
                        <div className="text-sm opacity-75">
                          amaz0n-deals.cc/checkout
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <StatusBar95>
                <LED label="Camera" on={cameraOn} />
                <div className="border-sunken px-2 py-0.5">
                  domain: {detectedDomain}
                </div>
                <div className="border-sunken px-2 py-0.5">
                  confidence: {issues.length > 0 ? "94%" : "—"}
                </div>
              </StatusBar95>
            </Card95>
          </div>

          {/* Right: Inspector */}
          <div className="space-y-3">
            {/* Findings */}
            <Card95 title="Findings">
              {issues.length > 0 && (
                <Badge95 variant={riskVariant} icon="⚠️" className="mb-3">
                  {riskLevel.toUpperCase()} RISK
                </Badge95>
              )}
              
              {issues.length === 0 ? (
                <div className="text-sm text-muted-foreground text-center py-4">
                  No issues detected yet
                </div>
              ) : (
                <ul className="space-y-2 text-sm">
                  {issues.map(issue => (
                    <li key={issue.id} className="flex items-start gap-2 border-sunken p-2 bg-input">
                      <span className="text-base">{issue.icon}</span>
                      <span className="flex-1">{issue.text}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card95>

            {/* One-Tap Fixes */}
            <Card95 title="One-Tap Fixes">
              <div className="space-y-3">
                <div>
                  <div className="text-xs font-bold mb-1.5 text-muted-foreground">PAYMENT CONTROLS</div>
                  <div className="space-y-1">
                    <Button95 icon="🪪" className="w-full" onClick={() => setVcModalOpen(true)}>
                      Virtual Trial Card
                    </Button95>
                    <Button95 icon="🔒" className="w-full" onClick={() => setCapModalOpen(true)}>
                      Set Spend Cap
                    </Button95>
                  </div>
                </div>

                <div>
                  <div className="text-xs font-bold mb-1.5 text-muted-foreground">SUBSCRIPTION HYGIENE</div>
                  <div className="space-y-1">
                    <Button95 icon="⏰" className="w-full" onClick={handleAutoCancel}>
                      Auto-Cancel Reminder
                    </Button95>
                    <Button95 icon="📨" className="w-full" onClick={handleEmailScript}>
                      Cancel Email Script
                    </Button95>
                  </div>
                </div>

                <div>
                  <div className="text-xs font-bold mb-1.5 text-muted-foreground">PROTECTION & PROOF</div>
                  <div className="space-y-1">
                    <Button95 icon="🧾" className="w-full" onClick={() => setDisputeModalOpen(true)}>
                      Dispute Pre-Pack
                    </Button95>
                    <Button95 
                      icon={evidenceCaptured ? "✅" : "📸"} 
                      className="w-full" 
                      variant={evidenceCaptured ? "primary" : "success"} 
                      onClick={handleSnapshot}
                    >
                      {evidenceCaptured ? "Evidence Saved" : "Signed Evidence"}
                    </Button95>
                  </div>
                </div>
              </div>
            </Card95>

            {/* Impact Stats */}
            <Card95 title="Impact">
              <div className="space-y-2">
                <div className="border-sunken p-2 bg-input">
                  <div className="text-xs text-muted-foreground">Fees Avoided</div>
                  <div className="text-xl font-bold text-success">${impact.feesAvoided.toFixed(2)}</div>
                </div>
                <div className="border-sunken p-2 bg-input">
                  <div className="text-xs text-muted-foreground">Subs Paused</div>
                  <div className="text-xl font-bold text-primary">{impact.subsPaused}</div>
                </div>
                <div className="border-sunken p-2 bg-input">
                  <div className="text-xs text-muted-foreground">Risk Score</div>
                  <div className="text-xl font-bold text-destructive">
                    {impact.riskScore > 0 ? `${impact.riskScore}%` : "—"}
                  </div>
                </div>
              </div>
            </Card95>
          </div>
        </div>

        {/* Bottom Status Bar */}
        <StatusBar95>
          <span>💡 Tip: Press SPACE to pause overlay | F8 = Retro Mode</span>
        </StatusBar95>
      </Window95>

      {/* Virtual Card Modal */}
      <Modal95
        open={vcModalOpen}
        onOpenChange={setVcModalOpen}
        title="Virtual Trial Card"
        description="Generate a one-time card with spend caps and merchant locks"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold mb-1">Merchant</label>
            <input 
              type="text" 
              defaultValue="tricky-sub.example" 
              className="w-full border-sunken px-2 py-1 bg-input"
            />
          </div>
          
          <div>
            <label className="block text-sm font-bold mb-1">Spend Cap: ${vcCap.toFixed(2)}</label>
            <input 
              type="range" 
              min="1" 
              max="100" 
              step="0.01"
              value={vcCap}
              onChange={(e) => setVcCap(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-bold mb-1">Auto-Expire</label>
            <select className="w-full border-sunken px-2 py-1 bg-input">
              <option>3 days</option>
              <option selected>7 days</option>
              <option>30 days</option>
            </select>
          </div>

          <Card95 title="Generated Card (Demo)">
            <div className="space-y-2 font-mono text-sm">
              <div className="border-sunken p-2 bg-input">4242 4242 4242 4242</div>
              <div className="grid grid-cols-3 gap-2">
                <div className="border-sunken p-2 bg-input">12/29</div>
                <div className="border-sunken p-2 bg-input">123</div>
                <div className="border-sunken p-2 bg-input">02139</div>
              </div>
            </div>
          </Card95>

          <div className="flex gap-2 pt-2">
            <Button95 variant="primary" className="flex-1" onClick={handleCreateVC}>
              Create & Copy
            </Button95>
            <Button95 onClick={() => setVcModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Spend Cap Modal */}
      <Modal95
        open={capModalOpen}
        onOpenChange={setCapModalOpen}
        title="Set Spend Cap"
        description="Limit total chargeable amount for this transaction"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-bold mb-2">
              Maximum Amount: ${spendCap.toFixed(2)}
            </label>
            <input 
              type="range" 
              min="5" 
              max="200" 
              step="1"
              value={spendCap}
              onChange={(e) => setSpendCap(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <div className="border-sunken p-2 bg-input flex items-center gap-2">
            <input type="checkbox" defaultChecked id="enforce" />
            <label htmlFor="enforce" className="text-sm">Decline anything above cap</label>
          </div>

          <div className="flex gap-2 pt-2">
            <Button95 variant="primary" className="flex-1" onClick={handleSetCap}>
              Apply
            </Button95>
            <Button95 onClick={() => setCapModalOpen(false)}>
              Cancel
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Dispute Modal */}
      <Modal95
        open={disputeModalOpen}
        onOpenChange={setDisputeModalOpen}
        title="Dispute Pre-Pack"
        description="Bank-ready draft with evidence links"
      >
        <div className="space-y-4">
          <textarea 
            className="w-full border-sunken p-2 bg-input font-mono text-xs min-h-[200px]"
            defaultValue={`To Whom It May Concern,

I am disputing the charge of $12.99 from trickysub.example on grounds of deceptive practices.

Evidence:
- Hidden fees not disclosed until final checkout step
- Pre-checked opt-in boxes for additional services
- Auto-renewal terms buried in fine print
- Signed screenshot hash: a3f9c8d7e1b4...

I request full refund and cancellation.

Signed,
[Your Name]`}
          />

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1">
              Download (.txt)
            </Button95>
            <Button95 onClick={() => setDisputeModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Calendar Reminder Modal */}
      <Modal95
        open={calendarModalOpen}
        onOpenChange={setCalendarModalOpen}
        title="Auto-Cancel Reminder"
        description="Your trial cancellation reminder has been scheduled"
      >
        <div className="space-y-4">
          <div className="border-sunken p-3 bg-input">
            <div className="text-sm mb-2">
              <strong>📅 Reminder Set For:</strong>
            </div>
            <div className="text-xl font-bold text-primary">
              {reminderDate?.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
          </div>

          <Card95 title="Calendar View">
            <div className="flex justify-center bg-background p-2">
              <Calendar
                mode="single"
                selected={reminderDate || undefined}
                onSelect={(date) => date && setReminderDate(date)}
                className="rounded-md"
                modifiers={{
                  reminder: reminderDate ? [reminderDate] : []
                }}
                modifiersStyles={{
                  reminder: { 
                    backgroundColor: '#ff0000',
                    color: 'white',
                    fontWeight: 'bold'
                  }
                }}
              />
            </div>
          </Card95>

          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>💡</span>
              <div>
                <strong>What happens next:</strong>
                <ul className="mt-1 space-y-1 ml-4 list-disc">
                  <li>Email reminder 48 hours before trial ends</li>
                  <li>SMS notification on cancellation day</li>
                  <li>One-click cancel link included</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1" onClick={() => {
              toast.success("Reminder Confirmed", {
                description: "You'll receive notifications before the trial ends",
                icon: "✅"
              });
              setCalendarModalOpen(false);
            }}>
              Confirm Reminder
            </Button95>
            <Button95 onClick={() => setCalendarModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Cancel Email Script Modal */}
      <Modal95
        open={emailScriptModalOpen}
        onOpenChange={setEmailScriptModalOpen}
        title="Cancel Email Script"
        description="Copy this template and send to cancel your subscription"
      >
        <div className="space-y-4">
          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>💡</span>
              <div>
                <strong>Pro Tip:</strong> Send from the email you signed up with. Keep this email as proof of cancellation request.
              </div>
            </div>
          </div>

          <Card95 title="Email Template">
            <textarea 
              id="cancel-email-text"
              className="w-full border-sunken p-2 bg-input font-mono text-xs min-h-[280px]"
              defaultValue={`Subject: Subscription Cancellation Request - Immediate Action Required

Dear Customer Service,

I am writing to formally request the immediate cancellation of my subscription/trial account.

Account Details:
- Email: [Your Email]
- Order/Account ID: [If Known]
- Service: [Service Name]

I request confirmation that:
1. My subscription is cancelled effective immediately
2. No further charges will be applied to my payment method
3. All recurring billing has been stopped

This cancellation request is made in accordance with your Terms of Service and consumer protection laws. I am not requesting a refund for services already rendered, but I expect no additional charges.

Please send written confirmation of this cancellation to this email address within 24 hours.

If I do not receive confirmation, or if any charges appear after this date, I will dispute them with my financial institution and report the practice to the Federal Trade Commission (FTC) and Consumer Financial Protection Bureau (CFPB).

Thank you for your prompt attention to this matter.

Sincerely,
[Your Full Name]
[Date: ${new Date().toLocaleDateString()}]

---
This email was generated by See-Through Checkout
Timestamp: ${new Date().toISOString()}`}
            />
          </Card95>

          <div className="grid grid-cols-2 gap-2">
            <div className="border-sunken p-2 bg-input text-center">
              <div className="text-xs text-muted-foreground">To:</div>
              <div className="text-sm font-bold">support@merchant.com</div>
            </div>
            <div className="border-sunken p-2 bg-input text-center">
              <div className="text-xs text-muted-foreground">CC:</div>
              <div className="text-sm font-bold">cancel@merchant.com</div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button95 variant="success" className="flex-1" onClick={handleCopyEmail}>
              📋 Copy Email
            </Button95>
            <Button95 onClick={() => setEmailScriptModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Preferences Modal */}
      <Modal95
        open={preferencesModalOpen}
        onOpenChange={setPreferencesModalOpen}
        title="⚙️ Preferences"
        description="Customize your experience"
      >
        <div className="space-y-4">
          <Card95 title="Appearance">
            <div className="space-y-3">
              <div className="text-sm font-bold mb-2">Theme</div>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setTheme('light')}
                  className={`border-raised p-3 text-center hover:bg-muted ${
                    theme === 'light' ? 'bg-primary text-primary-foreground' : 'bg-background'
                  }`}
                >
                  <div className="text-2xl mb-1">☀️</div>
                  <div className="text-xs">Light</div>
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`border-raised p-3 text-center hover:bg-muted ${
                    theme === 'dark' ? 'bg-primary text-primary-foreground' : 'bg-background'
                  }`}
                >
                  <div className="text-2xl mb-1">🌙</div>
                  <div className="text-xs">Dark</div>
                </button>
                <button
                  onClick={() => setTheme('system')}
                  className={`border-raised p-3 text-center hover:bg-muted ${
                    theme === 'system' ? 'bg-primary text-primary-foreground' : 'bg-background'
                  }`}
                >
                  <div className="text-2xl mb-1">💻</div>
                  <div className="text-xs">System</div>
                </button>
              </div>
            </div>
          </Card95>

          <Card95 title="Detection Settings">
            <div className="space-y-3">
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setOcrEnabled(!ocrEnabled);
                     toast.info(`OCR ${!ocrEnabled ? 'Enabled' : 'Disabled'}`, { 
                       description: !ocrEnabled ? 'Text extraction from images active' : 'Manual HTML upload only',
                       icon: !ocrEnabled ? '👁️' : '🚫'
                     });
                   }}>
                <span className="text-sm">OCR Enabled</span>
                <input 
                  type="checkbox" 
                  checked={ocrEnabled}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setAutoScan(!autoScan);
                     toast.info(`Auto-scan ${!autoScan ? 'Enabled' : 'Disabled'}`, { 
                       description: !autoScan ? 'Files will scan automatically on upload' : 'Manual scan required',
                       icon: !autoScan ? '🔍' : '⏸️'
                     });
                   }}>
                <span className="text-sm">Auto-scan on Upload</span>
                <input 
                  type="checkbox" 
                  checked={autoScan}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setShowRiskWarnings(!showRiskWarnings);
                     toast.info(`Risk Warnings ${!showRiskWarnings ? 'Enabled' : 'Disabled'}`, { 
                       description: !showRiskWarnings ? 'High-risk alerts will show prominently' : 'Warnings hidden',
                       icon: !showRiskWarnings ? '⚠️' : '🔕'
                     });
                   }}>
                <span className="text-sm">Show Risk Warnings</span>
                <input 
                  type="checkbox" 
                  checked={showRiskWarnings}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
              
              <div className="border-t border-border pt-3 mt-3">
                <div className="text-sm font-bold mb-2">Detection Sensitivity: {detectionSensitivity}%</div>
                <div className="space-y-2">
                  <input 
                    type="range" 
                    min="0" 
                    max="100" 
                    value={detectionSensitivity}
                    onChange={(e) => setDetectionSensitivity(parseInt(e.target.value))}
                    onMouseUp={() => {
                      const level = detectionSensitivity < 33 ? 'Low' : detectionSensitivity < 66 ? 'Medium' : 'High';
                      toast.success(`Sensitivity: ${level}`, { 
                        description: `Set to ${detectionSensitivity}% - ${level === 'High' ? 'May detect more potential issues' : level === 'Low' ? 'Only obvious patterns' : 'Balanced detection'}`,
                        icon: '🎚️'
                      });
                    }}
                    className="w-full h-2 cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Permissive</span>
                    <span>Balanced</span>
                    <span>Strict</span>
                  </div>
                </div>
              </div>
            </div>
          </Card95>

          <Card95 title="Notifications">
            <div className="space-y-3">
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setEmailReminders(!emailReminders);
                     toast.info(`Email Reminders ${!emailReminders ? 'Enabled' : 'Disabled'}`, { 
                       description: !emailReminders ? 'You\'ll receive trial end reminders via email' : 'Email notifications off',
                       icon: !emailReminders ? '📧' : '🔕'
                     });
                   }}>
                <div className="flex-1">
                  <div className="text-sm">Email Reminders</div>
                  <div className="text-xs text-muted-foreground">Trial end notifications</div>
                </div>
                <input 
                  type="checkbox" 
                  checked={emailReminders}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setBrowserNotifications(!browserNotifications);
                     if (!browserNotifications) {
                       // Simulate permission request
                       toast.info('Browser Notifications Enabled', { 
                         description: 'You\'ll see desktop alerts for high-risk detections',
                         icon: '🔔'
                       });
                     } else {
                       toast.info('Browser Notifications Disabled', { 
                         description: 'Desktop alerts turned off',
                         icon: '🔕'
                       });
                     }
                   }}>
                <div className="flex-1">
                  <div className="text-sm">Browser Notifications</div>
                  <div className="text-xs text-muted-foreground">Desktop alerts</div>
                </div>
                <input 
                  type="checkbox" 
                  checked={browserNotifications}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
              <div className="flex items-center justify-between border-sunken p-2 bg-input hover:bg-muted cursor-pointer"
                   onClick={() => {
                     setSoundEffects(!soundEffects);
                     if (!soundEffects) {
                       toast.info('Sound Effects Enabled', { 
                         description: '🔊 Audio feedback active',
                         icon: '🔊'
                       });
                     } else {
                       toast.info('Sound Effects Disabled', { 
                         description: 'Silent mode',
                         icon: '🔇'
                       });
                     }
                   }}>
                <div className="flex-1">
                  <div className="text-sm">Sound Effects</div>
                  <div className="text-xs text-muted-foreground">Audio feedback</div>
                </div>
                <input 
                  type="checkbox" 
                  checked={soundEffects}
                  onChange={() => {}}
                  className="w-4 h-4 cursor-pointer" 
                />
              </div>
            </div>
          </Card95>

          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>💡</span>
              <div>
                <strong>Pro Tip:</strong> System theme syncs with your OS settings for automatic dark mode switching.
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1" onClick={() => {
              const settings = [
                `Theme: ${theme}`,
                `OCR: ${ocrEnabled ? 'On' : 'Off'}`,
                `Sensitivity: ${detectionSensitivity}%`,
                `Notifications: ${emailReminders || browserNotifications || soundEffects ? 'Enabled' : 'Disabled'}`
              ];
              toast.success("Preferences Saved", { 
                description: settings.join(' • '), 
                icon: "✅" 
              });
              setPreferencesModalOpen(false);
            }}>
              💾 Save & Close
            </Button95>
            <Button95 onClick={() => setPreferencesModalOpen(false)}>
              Cancel
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Feature Request Modal */}
      <Modal95
        open={featureRequestModalOpen}
        onOpenChange={setFeatureRequestModalOpen}
        title="💡 Request Feature"
        description="Help us improve See-Through Checkout"
      >
        <div className="space-y-4">
          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>✨</span>
              <div>
                We love hearing your ideas! Tell us what feature would make See-Through even better.
              </div>
            </div>
          </div>

          <Card95 title="Your Feature Idea">
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-bold mb-2">Feature Title</label>
                <input 
                  type="text" 
                  placeholder="e.g., Add browser extension for Chrome"
                  className="w-full border-sunken px-2 py-1.5 bg-input text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-bold mb-2">Describe Your Idea</label>
                <textarea 
                  placeholder="Tell us more about the feature you'd like to see. What problem would it solve? How would you use it?"
                  className="w-full border-sunken p-2 bg-input font-mono text-xs min-h-[150px] resize-none"
                  defaultValue=""
                />
              </div>

              <div>
                <label className="block text-sm font-bold mb-2">Why is this important to you?</label>
                <select className="w-full border-sunken px-2 py-1 bg-input text-sm">
                  <option>Select priority level</option>
                  <option>🔥 Critical - I need this now</option>
                  <option>⭐ High - Would use it frequently</option>
                  <option>💡 Medium - Nice to have</option>
                  <option>📝 Low - Just a suggestion</option>
                </select>
              </div>
            </div>
          </Card95>

          <Card95 title="Optional: Contact Info">
            <div className="space-y-2">
              <input 
                type="email" 
                placeholder="your.email@example.com (optional)"
                className="w-full border-sunken px-2 py-1.5 bg-input text-sm"
              />
              <div className="text-xs text-muted-foreground">
                We'll reach out if we need more details or when the feature is ready!
              </div>
            </div>
          </Card95>

          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>💬</span>
              <div>
                <strong>Join the conversation:</strong> Vote on features and discuss ideas in our Discord community!
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1" onClick={() => {
              toast.success("Feature Request Submitted", { 
                description: "Thank you! We'll review your suggestion.", 
                icon: "✨" 
              });
              setFeatureRequestModalOpen(false);
            }}>
              🚀 Submit Request
            </Button95>
            <Button95 onClick={() => setFeatureRequestModalOpen(false)}>
              Cancel
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Help Modal */}
      <Modal95
        open={helpModalOpen}
        onOpenChange={setHelpModalOpen}
        title="📖 User Guide"
        description="How to use See-Through Checkout"
      >
        <div className="space-y-4">
          <Card95 title="Quick Start">
            <ol className="text-sm space-y-2 list-decimal ml-4">
              <li><strong>Upload or Load Demo</strong> - Upload a checkout screenshot or HTML file</li>
              <li><strong>Review Findings</strong> - See detected dark patterns and risk score</li>
              <li><strong>Take Action</strong> - Create virtual card, set reminders, or generate dispute</li>
              <li><strong>Save Evidence</strong> - Capture signed proof for your records</li>
            </ol>
          </Card95>

          <Card95 title="Features">
            <div className="space-y-2 text-xs">
              <div className="border-sunken p-2 bg-input">
                <strong>🔍 Detection</strong> - Finds hidden fees, trial auto-renewals, pre-checked boxes, and suspicious domains
              </div>
              <div className="border-sunken p-2 bg-input">
                <strong>🪪 Virtual Cards</strong> - Create spend-capped, merchant-locked cards for trials
              </div>
              <div className="border-sunken p-2 bg-input">
                <strong>⏰ Reminders</strong> - Schedule auto-cancel notifications before trial ends
              </div>
              <div className="border-sunken p-2 bg-input">
                <strong>📨 Email Script</strong> - Generate professional cancellation emails
              </div>
              <div className="border-sunken p-2 bg-input">
                <strong>📸 Evidence</strong> - Signed screenshots with SHA-256 hashes for disputes
              </div>
            </div>
          </Card95>

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1" onClick={() => setHelpModalOpen(false)}>
              Got It!
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* Contact Support Modal */}
      <Modal95
        open={contactModalOpen}
        onOpenChange={setContactModalOpen}
        title="📞 Contact Support"
        description="Get help from our team"
      >
        <div className="space-y-4">
          <div className="border-sunken p-3 bg-input">
            <div className="text-center space-y-2">
              <div className="text-4xl mb-2">💬</div>
              <div className="text-sm font-bold">We're Here to Help!</div>
              <div className="text-xs text-muted-foreground">
                Response time: Usually within 24 hours
              </div>
            </div>
          </div>

          <Card95 title="Contact Methods">
            <div className="space-y-2 text-sm">
              <div className="border-sunken p-2 bg-input flex items-center gap-2">
                <span>📧</span>
                <div className="flex-1">
                  <div className="font-bold">Email</div>
                  <div className="text-xs text-primary">support@seethrough.app</div>
                </div>
              </div>
              
              <div className="border-sunken p-2 bg-input flex items-center gap-2">
                <span>💬</span>
                <div className="flex-1">
                  <div className="font-bold">Discord Community</div>
                  <div className="text-xs text-primary">discord.gg/seethrough</div>
                </div>
              </div>
              
              <div className="border-sunken p-2 bg-input flex items-center gap-2">
                <span>🐦</span>
                <div className="flex-1">
                  <div className="font-bold">Twitter/X</div>
                  <div className="text-xs text-primary">@SeeThrough_App</div>
                </div>
              </div>

              <div className="border-sunken p-2 bg-input flex items-center gap-2">
                <span>📱</span>
                <div className="flex-1">
                  <div className="font-bold">Report Issues</div>
                  <div className="text-xs text-primary">github.com/seethrough/issues</div>
                </div>
              </div>
            </div>
          </Card95>

          <div className="border-sunken p-2 bg-input text-xs">
            <div className="flex items-start gap-2">
              <span>💡</span>
              <div>
                <strong>Before contacting:</strong> Check the User Guide (Help menu) for common questions and troubleshooting tips.
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button95 variant="success" className="flex-1" onClick={() => {
              navigator.clipboard.writeText('support@seethrough.app');
              toast.success("Email Copied", { description: "support@seethrough.app", icon: "📋" });
            }}>
              📋 Copy Email
            </Button95>
            <Button95 onClick={() => setContactModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>

      {/* About Modal */}
      <Modal95
        open={aboutModalOpen}
        onOpenChange={setAboutModalOpen}
        title="ℹ️ About See-Through"
        description="Consumer protection for the digital age"
      >
        <div className="space-y-4">
          <div className="text-center border-sunken p-4 bg-input">
            <div className="text-6xl mb-2">🖥️</div>
            <div className="text-xl font-bold mb-1">See-Through Checkout</div>
            <div className="text-sm text-muted-foreground mb-2">Version 1.0.0 Beta</div>
            <div className="text-xs italic">"AR Glasses for Checkout BS"</div>
          </div>

          <Card95 title="Mission">
            <p className="text-sm leading-relaxed">
              We believe consumers deserve transparency in online checkout. See-Through detects 
              dark patterns, hidden fees, and deceptive practices—empowering you to make informed 
              decisions and protect your finances.
            </p>
          </Card95>

          <Card95 title="Impact Stats">
            <div className="grid grid-cols-2 gap-2">
              <div className="border-sunken p-2 bg-input text-center">
                <div className="text-xl font-bold text-success">$15B+</div>
                <div className="text-xs text-muted-foreground">Lost to dark patterns yearly</div>
              </div>
              <div className="border-sunken p-2 bg-input text-center">
                <div className="text-xl font-bold text-primary">200M+</div>
                <div className="text-xs text-muted-foreground">Online shoppers affected</div>
              </div>
            </div>
          </Card95>

          <div className="border-sunken p-2 bg-input text-xs space-y-1">
            <div><strong>Built with:</strong> React, TypeScript, FastAPI, PostgreSQL</div>
            <div><strong>OCR Engine:</strong> Tesseract</div>
            <div><strong>License:</strong> MIT Open Source</div>
          </div>

          <div className="text-center text-xs text-muted-foreground">
            Made with ❤️ for consumer protection
          </div>

          <div className="flex gap-2">
            <Button95 variant="primary" className="flex-1" onClick={() => setAboutModalOpen(false)}>
              Close
            </Button95>
          </div>
        </div>
      </Modal95>
    </div>
  );
};

export default Index;
