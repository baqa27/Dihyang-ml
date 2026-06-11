import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useThemeColors } from "../hooks/useThemeColors";
import { useEffect } from "react";
import { Building2, MessageSquare, MapPin, Mail, Phone } from "lucide-react";
import { motion } from "motion/react";

export default function Perusahaan() {
  const c = useThemeColors();

  // Scroll to top on load
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Handle hash scrolling
  useEffect(() => {
    const hash = window.location.hash;
    if (hash) {
      setTimeout(() => {
        const element = document.getElementById(hash.substring(1));
        if (element) {
          element.scrollIntoView({ behavior: "smooth" });
        }
      }, 500);
    }
  }, []);

  const sections = [
    {
      id: "tentang",
      title: "Tentang Kami",
      icon: <Building2 className="w-6 h-6" />,
      content: (
        <div className="space-y-4 text-sm opacity-90 leading-relaxed">
          <p>
            Dihyang adalah platform wisata cerdas yang dirancang khusus untuk mengeksplorasi keindahan Dataran Tinggi Dieng. 
            Misi kami adalah memberikan pengalaman wisata terbaik bagi setiap penjelajah dengan mengintegrasikan teknologi 
            modern seperti Prediksi Cuaca Real-time dan Asisten AI cerdas (DITA).
          </p>
          <p>
            Berawal dari kecintaan kami terhadap kekayaan alam dan budaya Dieng, tim Dihyang berkomitmen untuk 
            memudahkan wisatawan dalam merencanakan perjalanan mereka. Kami percaya bahwa setiap perjalanan harus 
            menjadi pengalaman yang aman, nyaman, dan tak terlupakan.
          </p>
        </div>
      )
    },
    {
      id: "hubungi",
      title: "Hubungi Kami",
      icon: <MessageSquare className="w-6 h-6" />,
      content: (
        <div className="space-y-6">
          <p className="text-sm opacity-90">
            Kami selalu siap mendengar dari Anda. Jika Anda memiliki pertanyaan, saran, atau sekadar ingin menyapa, 
            jangan ragu untuk menghubungi tim kami melalui saluran berikut:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl flex items-start gap-4" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
              <div className="p-2 rounded-lg" style={{ backgroundColor: "rgba(79,209,197,0.1)", color: c.primary }}>
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold mb-1">Kantor Pusat</h4>
                <p className="text-sm opacity-80">Wonosobo, Jawa Tengah, Indonesia</p>
              </div>
            </div>
            <div className="p-4 rounded-xl flex items-start gap-4" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
              <div className="p-2 rounded-lg" style={{ backgroundColor: "rgba(79,209,197,0.1)", color: c.primary }}>
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold mb-1">Email</h4>
                <p className="text-sm opacity-80">dihyang@smartwisata.id</p>
              </div>
            </div>
            <div className="p-4 rounded-xl flex items-start gap-4 md:col-span-2" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
              <div className="p-2 rounded-lg" style={{ backgroundColor: "rgba(79,209,197,0.1)", color: c.primary }}>
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold mb-1">Telepon & WhatsApp</h4>
                <p className="text-sm opacity-80">+62 21 1234 5678</p>
              </div>
            </div>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="min-h-screen transition-colors duration-300" style={{ backgroundColor: c.bgBase, color: c.textPrimary }}>
      <Navbar />
      
      <div className="pt-24 pb-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="mb-10 text-center"
        >
          <h1 className="text-3xl md:text-4xl font-bold mb-4" style={{ color: c.primary }}>Perusahaan</h1>
          <p className="text-lg opacity-80">Kenali kami lebih dekat dan mari terhubung.</p>
        </motion.div>

        <div className="space-y-12">
          {sections.map((section, index) => (
            <motion.div 
              key={section.id} 
              id={section.id} 
              className="scroll-mt-24"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 + (index * 0.1), ease: "easeOut" }}
            >
              <div className="flex items-center gap-3 mb-6 pb-2 border-b" style={{ borderColor: c.border }}>
                <div style={{ color: c.primary }}>{section.icon}</div>
                <h2 className="text-2xl font-bold">{section.title}</h2>
              </div>
              <div className="pl-0 md:pl-9">
                {section.content}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      <Footer />
    </div>
  );
}
