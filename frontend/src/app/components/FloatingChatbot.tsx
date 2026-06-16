import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Send, X, RotateCcw, ChevronDown } from "lucide-react";
import { useThemeColors } from "../hooks/useThemeColors";

type Message = {
  id: number;
  role: "bot" | "user";
  text: string;
  time: string;
};

const quickReplies = [
  { text: "🌡️ Cuaca Dieng hari ini?", query: "Bagaimana cuaca di Dieng hari ini?" },
  { text: "🏛️ Tempat wisata terbaik", query: "Apa saja tempat wisata terbaik di Dieng?" },
  { text: "🎟️ Harga tiket Candi Arjuna", query: "Berapa harga tiket Candi Arjuna?" },
  { text: "🌄 Sunrise terbaik Dieng", query: "Di mana spot sunrise terbaik di Dieng?" },
  { text: "🏨 Penginapan dekat Dieng", query: "Rekomendasikan penginapan di Dieng" },
  { text: "🚌 Cara ke Dieng dari Jogja", query: "Bagaimana cara ke Dieng dari Yogyakarta?" },
];

const initialMessages: Message[] = [
  {
    id: 1,
    role: "bot",
    text: "Halo! Saya **DITA** 👋\n*Dieng Intelligence Tourism Assistant*\n\nSaya siap membantu perjalanan Anda ke Dataran Tinggi Dieng! Tanyakan apa saja tentang wisata, cuaca, tiket, atau penginapan di Dieng 🏔️",
    time: "Sekarang",
  },
];

const nowTime = () => {
  const d = new Date();
  return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
};

function parseMarkdown(text: string) {
  return text.split("\n").map((line, i) => {
    let html = line
      .replace(/\*\*(.*?)\*\*/g, "<strong class='font-semibold'>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>");
      
    // Remove list markers and long dashes at the start of a line
    html = html.replace(/^[\s]*[\*\-\•—]\s+/g, "");
    
    // Remove any remaining stray * or long dashes
    html = html.replace(/\*/g, "");
    html = html.replace(/—/g, "-");

    return <div key={i} className="mb-1 last:mb-0" dangerouslySetInnerHTML={{ __html: html || "&nbsp;" }} />;
  });
}

function parseMessageWithOptions(text: string) {
  const match = text.match(/\[OPSI:\s*(.*?)\]/i);
  let cleanText = text;
  let options: string[] = [];

  if (match) {
    cleanText = text.replace(match[0], "").trim();
    options = match[1].split(",").map(s => s.trim()).filter(s => s);
  }

  return { cleanText, options };
}

export default function FloatingChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const c = useThemeColors();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen) setTimeout(() => inputRef.current?.focus(), 300);
  }, [isOpen]);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    setShowQuickReplies(false);
    
    setMessages((prev) => [...prev, { id: Date.now(), role: "user", text, time: nowTime() }]);
    setInput("");
    setIsTyping(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          history: messages.map(m => ({
            role: m.role,
            content: m.text
          }))
        }),
      });
      const data = await res.json();
      const responseText = data.reply || "Maaf, terjadi kesalahan pada server.";
      
      setIsTyping(false);
      setMessages((prev) => [...prev, { id: Date.now(), role: "bot", text: responseText, time: nowTime() }]);
    } catch (error) {
      console.error(error);
      setIsTyping(false);
      setMessages((prev) => [...prev, { id: Date.now(), role: "bot", text: "Maaf, server backend tidak dapat dihubungi. Pastikan server berjalan di port 8000.", time: nowTime() }]);
    }
  };

  const handleReset = () => {
    setMessages(initialMessages);
    setShowQuickReplies(true);
  };

  return (
    <div className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 flex flex-col items-end gap-3 w-[calc(100%-2rem)] sm:w-auto">
      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.85, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.85, y: 20 }}
            transition={{ type: "spring", damping: 22, stiffness: 300 }}
            className="w-full sm:w-96 rounded-3xl overflow-hidden shadow-2xl"
            style={{
              border: `1px solid ${c.border}`,
              boxShadow: "0 25px 60px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.05)",
            }}
          >
            {/* Header */}
            <div
              className="px-5 py-4 flex items-center justify-between"
              style={{ background: c.gradientChatHeader }}
            >
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div
                    className="w-10 h-10 rounded-2xl flex items-center justify-center shadow-md"
                    style={{ background: c.gradientPrimary }}
                  >
                    <span className="text-lg">🏔️</span>
                  </div>
                  <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-green-400 border-2" style={{ borderColor: c.navBg }} />
                </div>
                <div>
                  <div className="text-white font-bold text-sm">DITA</div>
                  <div className="text-[10px]" style={{ color: c.primaryLight }}>
                    Dieng Intelligence Tourism Assistant
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={handleReset}
                  className="p-1.5 rounded-lg transition-colors hover:bg-white/10"
                  title="Reset"
                >
                  <RotateCcw className="w-3.5 h-3.5 text-white opacity-70 hover:opacity-100" />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-lg transition-colors hover:bg-white/10"
                >
                  <ChevronDown className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div
              className="h-72 overflow-y-auto p-4 space-y-3"
              style={{ backgroundColor: c.bgInput }}
            >
              {messages.map((msg) => {
                const { cleanText, options } = parseMessageWithOptions(msg.text);
                return (
                  <div key={msg.id} className="flex flex-col gap-1.5">
                    <div
                      className={`flex items-end gap-2 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                    >
                      <div
                        className="w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm text-sm"
                        style={{
                          background: msg.role === "bot" ? c.gradientPrimary : c.gradientAccent,
                        }}
                      >
                        {msg.role === "bot" ? "🏔️" : "👤"}
                      </div>
                      <div
                        className="max-w-[220px] text-xs leading-relaxed px-3 py-2.5 shadow-sm"
                        style={{
                          backgroundColor: msg.role === "user" ? c.navBg : c.bgSurface,
                          color: msg.role === "user" ? "#ffffff" : c.textPrimary,
                          borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                        }}
                      >
                        {parseMarkdown(cleanText)}
                      </div>
                    </div>
                    {/* Bubbles Opsi Khusus */}
                    {options.length > 0 && msg.role === "bot" && (
                      <div className="flex flex-wrap gap-2 ml-9 mt-1 max-w-[230px]">
                        {options.map((opt, i) => (
                          <button
                            key={i}
                            onClick={() => sendMessage(opt)}
                            className="text-[10px] px-2.5 py-1.5 rounded-lg border transition-all hover:scale-[1.05] shadow-sm font-medium"
                            style={{
                              backgroundColor: c.bgSurface,
                              color: c.primary,
                              borderColor: c.primary,
                            }}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}

              {isTyping && (
                <div className="flex items-end gap-2">
                  <div
                    className="w-7 h-7 rounded-xl flex items-center justify-center text-sm shadow-sm"
                    style={{ background: c.gradientPrimary }}
                  >
                    🏔️
                  </div>
                  <div
                    className="px-3 py-2.5 rounded-2xl rounded-bl-sm shadow-sm"
                    style={{ backgroundColor: c.bgSurface }}
                  >
                    <div className="flex gap-1 items-center h-3">
                      {[0, 1, 2].map((i) => (
                        <span
                          key={i}
                          className="w-1.5 h-1.5 rounded-full animate-bounce"
                          style={{ backgroundColor: c.primary, animationDelay: `${i * 0.15}s` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Quick Replies */}
              {showQuickReplies && messages.length === 1 && (
                <div className="space-y-1.5 pt-1">
                  {quickReplies.map((q) => (
                    <button
                      key={q.query}
                      onClick={() => sendMessage(q.query)}
                      className="block w-full text-left text-xs px-3 py-2 rounded-xl transition-all hover:scale-[1.02] border"
                      style={{
                        backgroundColor: c.bgSurface,
                        color: c.successText,
                        borderColor: c.successBorder,
                      }}
                    >
                      {q.text}
                    </button>
                  ))}
                </div>
              )}

              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div
              className="p-3 border-t"
              style={{ backgroundColor: c.bgSurface, borderColor: c.border }}
            >
              <div
                className="flex items-center gap-2 px-3 py-2 rounded-2xl border"
                style={{ borderColor: c.border, backgroundColor: c.bgInput }}
              >
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Tanya DITA tentang Dieng..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
                  className="flex-1 bg-transparent outline-none text-xs"
                  style={{ color: c.textPrimary }}
                />
                <button
                  onClick={() => sendMessage(input)}
                  disabled={!input.trim()}
                  className="w-7 h-7 rounded-xl flex items-center justify-center text-white transition-all hover:scale-105 disabled:opacity-40"
                  style={{ background: c.gradientPrimary }}
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        className="relative flex items-center gap-2 md:gap-2.5 p-3 md:pl-4 md:pr-5 md:py-3 rounded-full text-white font-semibold shadow-2xl transition-all"
        style={{
          background: isOpen
            ? "linear-gradient(135deg, #374151, #1f2937)"
            : c.gradientNav,
          boxShadow: isOpen
            ? "0 8px 30px rgba(0,0,0,0.3)"
            : `0 8px 30px rgba(27,63,62,0.5), 0 0 0 4px ${c.primaryGlow}`,
        }}
      >
        {/* Pulse ring when closed */}
        {!isOpen && (
          <span
            className="absolute inset-0 rounded-full animate-ping opacity-20"
            style={{ backgroundColor: c.primary }}
          />
        )}

        <div
          className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ background: "rgba(255,255,255,0.15)" }}
        >
          {isOpen ? (
            <X className="w-4 h-4 text-white" />
          ) : (
            <span className="text-base">🏔️</span>
          )}
        </div>

        <div className="text-left hidden md:block">
          <div className="text-sm font-bold leading-tight">DITA</div>
          <div className="text-[10px] leading-tight opacity-80">
            {isOpen ? "Tutup Chat" : "Tanya wisata Dieng"}
          </div>
        </div>

        {/* Unread dot when closed */}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-400 border-2 border-white flex items-center justify-center">
            <span className="text-[8px] font-bold text-amber-900">1</span>
          </span>
        )}
      </motion.button>
    </div>
  );
}
