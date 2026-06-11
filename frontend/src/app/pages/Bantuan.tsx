import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { useThemeColors } from "../hooks/useThemeColors";
import { useEffect } from "react";
import { HelpCircle, BookOpen, Shield, FileText } from "lucide-react";
import { motion } from "motion/react";

export default function Bantuan() {
  const c = useThemeColors();

  // Scroll to top on load
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Handle hash scrolling if a user comes with a hash in URL (e.g. /bantuan#faq)
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
      id: "faq",
      title: "FAQ (Pertanyaan yang Sering Diajukan)",
      icon: <HelpCircle className="w-6 h-6" />,
      content: (
        <div className="space-y-4">
          <div className="p-4 rounded-xl" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
            <h4 className="font-bold mb-2">Bagaimana cara menggunakan DITA AI?</h4>
            <p className="text-sm opacity-80">Anda dapat menggunakan DITA AI melalui fitur Asisten Cerdas di halaman utama. Cukup ketik pertanyaan Anda seputar wisata Dieng, dan DITA akan membantu menjawabnya.</p>
          </div>
          <div className="p-4 rounded-xl" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
            <h4 className="font-bold mb-2">Apakah prediksi cuaca selalu akurat?</h4>
            <p className="text-sm opacity-80">Prediksi cuaca kami diperbarui secara real-time dari sumber terpercaya. Namun, cuaca pegunungan dapat berubah dengan cepat, sehingga kami menyarankan Anda untuk selalu bersiap menghadapi suhu dingin.</p>
          </div>
          <div className="p-4 rounded-xl" style={{ backgroundColor: c.bgCard, border: `1px solid ${c.border}` }}>
            <h4 className="font-bold mb-2">Apakah aplikasi ini berbayar?</h4>
            <p className="text-sm opacity-80">Aplikasi Dihyang dapat digunakan secara gratis untuk merencanakan perjalanan Anda ke Dataran Tinggi Dieng.</p>
          </div>
        </div>
      )
    },
    {
      id: "panduan",
      title: "Panduan Pengguna",
      icon: <BookOpen className="w-6 h-6" />,
      content: (
        <div className="space-y-4 text-sm opacity-90 leading-relaxed">
          <p>Selamat datang di Dihyang! Berikut adalah panduan singkat untuk memaksimalkan fitur kami:</p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Beranda:</strong> Temukan informasi umum dan fitur utama.</li>
            <li><strong>Cuaca:</strong> Pantau suhu dan kelembapan real-time di berbagai lokasi di Dieng sebelum memulai perjalanan.</li>
            <li><strong>Rute & Navigasi:</strong> Lihat rekomendasi tempat wisata, estimasi waktu, dan jalur tempuh yang disarankan.</li>
            <li><strong>Smart Itinerary:</strong> Buat rencana perjalanan otomatis yang disesuaikan dengan preferensi waktu dan tempat Anda.</li>
            <li><strong>DITA AI:</strong> Tanyakan apa saja seputar tips perjalanan, pakaian yang disarankan, atau sejarah tempat wisata.</li>
          </ul>
        </div>
      )
    },
    {
      id: "privasi",
      title: "Kebijakan Privasi",
      icon: <Shield className="w-6 h-6" />,
      content: (
        <div className="space-y-4 text-sm opacity-90 leading-relaxed">
          <p>Kami sangat menghargai privasi Anda. Kebijakan ini menjelaskan bagaimana kami mengumpulkan, menggunakan, dan melindungi informasi pribadi Anda:</p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Pengumpulan Data:</strong> Kami hanya mengumpulkan data yang diperlukan untuk memberikan pengalaman pengguna yang lebih baik, seperti preferensi wisata dan history percakapan dengan DITA AI.</li>
            <li><strong>Penggunaan Data:</strong> Data Anda digunakan semata-mata untuk mempersonalisasi rekomendasi rute dan itinerary.</li>
            <li><strong>Keamanan:</strong> Kami menerapkan standar keamanan terkini untuk melindungi data Anda dari akses yang tidak sah.</li>
            <li><strong>Pihak Ketiga:</strong> Kami tidak menjual atau membagikan data pribadi Anda kepada pihak ketiga untuk tujuan pemasaran tanpa izin Anda.</li>
          </ul>
        </div>
      )
    },
    {
      id: "syarat",
      title: "Syarat & Ketentuan",
      icon: <FileText className="w-6 h-6" />,
      content: (
        <div className="space-y-4 text-sm opacity-90 leading-relaxed">
          <p>Dengan menggunakan platform Dihyang, Anda menyetujui syarat dan ketentuan berikut:</p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Penggunaan Layanan:</strong> Layanan ini ditujukan untuk membantu wisatawan merencanakan perjalanan ke Dieng. Pengguna dilarang menggunakan platform ini untuk tindakan melanggar hukum.</li>
            <li><strong>Akurasi Informasi:</strong> Meskipun kami berusaha memberikan informasi seakurat mungkin, jadwal wisata, cuaca, dan harga tiket di lokasi dapat berubah sewaktu-waktu.</li>
            <li><strong>Tanggung Jawab:</strong> Dihyang tidak bertanggung jawab atas kerugian materi atau non-materi yang mungkin timbul akibat kejadian di luar kendali kami selama perjalanan Anda.</li>
            <li><strong>Perubahan Syarat:</strong> Kami berhak mengubah syarat dan ketentuan ini kapan saja. Perubahan akan diinformasikan melalui halaman ini.</li>
          </ul>
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
          <h1 className="text-3xl md:text-4xl font-bold mb-4" style={{ color: c.primary }}>Pusat Bantuan</h1>
          <p className="text-lg opacity-80">Temukan jawaban, panduan, dan informasi kebijakan kami di bawah ini.</p>
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
