import React, { useState, useEffect, useMemo } from 'react';
import { 
  LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { 
  Package, TrendingDown, ShieldCheck, Activity, ArrowDownRight, ArrowUpRight,
  Zap, Globe, IndianRupee, MapPin, Languages, Radio, X, Send, User, Cpu, ShieldAlert, ArrowLeft
} from 'lucide-react';
import './Dashboard.css';

// --- Mock Data ---
const generateTrendData = () => Array.from({ length: 30 }, (_, i) => ({
  day: `Day ${i+1}`,
  withoutMAVVE: 25 + Math.random() * 5,
  withMAVVE: i < 15 ? 25 + Math.random() * 5 : 15 + Math.random() * 3
}));

const agentPerformanceData = [
  { name: 'Address Agent', success: 85, failed: 15 },
  { name: 'Intent Agent', success: 92, failed: 8 },
  { name: 'Prepaid Agent', success: 78, failed: 22 },
];

const initialSavings = [
  { id: 'ORD-098', user: 'Priya D.', saved: '₹499', agent: 'Intent Agent' },
  { id: 'ORD-097', user: 'Rahul T.', saved: '₹1,299', agent: 'Prepaid Agent' },
  { id: 'ORD-096', user: 'Amit P.', saved: '₹349', agent: 'Address Agent' },
];

const initialConversations = [
  { id: 'ORD-101', user: 'Ramesh K.', agent: 'Address Agent', status: 'Active', time: 'Just now' },
  { id: 'ORD-102', user: 'Sunita M.', agent: 'Intent Agent', status: 'Awaiting', time: '2m ago' },
  { id: 'ORD-103', user: 'Vikram S.', agent: 'Prepaid Agent', status: 'Escalated', time: '5m ago' },
];

const recentSavings = [
  { id: 'ORD-098', user: 'Priya D.', saved: '₹499', agent: 'Intent Agent' },
  { id: 'ORD-097', user: 'Rahul T.', saved: '₹1,299', agent: 'Prepaid Agent' },
  { id: 'ORD-096', user: 'Amit P.', saved: '₹349', agent: 'Address Agent' },
];

const tickerEvents = [
  { text: 'ORD-4192 intercepted — Address Agent resolving landmark', color: '#f59e0b' },
  { text: 'ORD-3810 validated — Intent confirmed in Hindi voice', color: '#10b981' },
  { text: 'ORD-2911 converted COD → UPI — Saved ₹420', color: '#10b981' },
  { text: 'ORD-5501 flagged — High RTO risk score 0.89', color: '#ef4444' },
  { text: 'ORD-7233 dispatched — Address verified via Bhashini ASR', color: '#10b981' },
  { text: 'ORD-1099 escalated — User unresponsive after 3 rounds', color: '#ef4444' },
  { text: 'ORD-6614 converted — Prepaid Agent offered ₹65 discount', color: '#10b981' },
  { text: 'ORD-8820 validated — Bengali voice confirmation received', color: '#3b82f6' },
];

const languages = [
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', flag: '🚩' },
  { code: 'bn', name: 'Bengali', flag: '🐅' },
  { code: 'te', name: 'Telugu', flag: '🌾' },
  { code: 'ta', name: 'Tamil', flag: '🏛️' },
  { code: 'kn', name: 'Kannada', flag: '🪷' },
  { code: 'ml', name: 'Malayalam', flag: '🌴' },
  { code: 'gu', name: 'Gujarati', flag: '🦁' },
  { code: 'pa', name: 'Punjabi', flag: '🌾' },
  { code: 'or', name: 'Odia', flag: '🏖️' },
  { code: 'as', name: 'Assamese', flag: '🦏' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
];

// India map hotspot data (state-level RTO rates)
const mapHotspots = [
  { state: 'UP', x: 58, y: 32, rto: 32, orders: '4.2L' },
  { state: 'Bihar', x: 68, y: 33, rto: 28, orders: '2.8L' },
  { state: 'WB', x: 75, y: 38, rto: 24, orders: '3.1L' },
  { state: 'MP', x: 52, y: 42, rto: 22, orders: '1.9L' },
  { state: 'Rajasthan', x: 42, y: 30, rto: 26, orders: '2.5L' },
  { state: 'Maharashtra', x: 45, y: 52, rto: 18, orders: '5.1L' },
  { state: 'Gujarat', x: 35, y: 42, rto: 15, orders: '2.2L' },
  { state: 'TN', x: 55, y: 72, rto: 12, orders: '3.8L' },
  { state: 'Karnataka', x: 48, y: 65, rto: 14, orders: '2.9L' },
  { state: 'AP', x: 58, y: 62, rto: 20, orders: '1.7L' },
  { state: 'Odisha', x: 68, y: 48, rto: 25, orders: '1.4L' },
  { state: 'Jharkhand', x: 68, y: 38, rto: 30, orders: '1.1L' },
  { state: 'Delhi', x: 52, y: 25, rto: 10, orders: '6.2L' },
  { state: 'Punjab', x: 47, y: 20, rto: 16, orders: '1.8L' },
  { state: 'Assam', x: 85, y: 30, rto: 35, orders: '0.8L' },
];

// Savings over time area chart data
const savingsAreaData = Array.from({ length: 12 }, (_, i) => ({
  month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
  savings: Math.floor(8 + Math.random() * 4),
  orders: Math.floor(12 + Math.random() * 6),
}));

// --- CountUp Hook ---
const useCountUp = (end, duration = 1500) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let startTime = null;
    const animate = (time) => {
      if (!startTime) startTime = time;
      const progress = Math.min((time - startTime) / duration, 1);
      setCount(Math.floor(progress * end));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration]);
  return count;
};

const translations = {
  en: {
    impactTitle: "MAVVE Financial Impact",
    impactSubtitle: "Projected annual savings from RTO mitigation",
    annualSavings: "Annual Savings",
    ordersSalvaged: "Orders Salvaged",
    rtoReduction: "RTO Reduction",
    languages: "Languages",
    totalOrders: "Total Orders (Today)",
    avgRto: "Avg RTO Rate",
    savedBy: "Saved by MAVVE",
    activeSessions: "Active Agent Sessions"
  },
  hi: {
    impactTitle: "MAVVE वित्तीय प्रभाव",
    impactSubtitle: "RTO शमन से अनुमानित वार्षिक बचत",
    annualSavings: "वार्षिक बचत",
    ordersSalvaged: "बचाए गए ऑर्डर्स",
    rtoReduction: "RTO में कमी",
    languages: "भाषाएँ",
    totalOrders: "कुल ऑर्डर्स (आज)",
    avgRto: "औसत RTO दर",
    savedBy: "MAVVE द्वारा बचत",
    activeSessions: "सक्रिय एजेंट सत्र"
  },
  mr: {
    impactTitle: "MAVVE आर्थिक प्रभाव",
    impactSubtitle: "RTO कमी केल्यामुळे अंदाजित वार्षिक बचत",
    annualSavings: "वार्षिक बचत",
    ordersSalvaged: "वाचवलेले ऑर्डर्स",
    rtoReduction: "RTO मध्ये घट",
    languages: "भाषा",
    totalOrders: "एकूण ऑर्डर्स (आज)",
    avgRto: "सरासरी RTO दर",
    savedBy: "MAVVE द्वारे बचत",
    activeSessions: "सक्रिय एजंट सत्रे"
  },
  bn: {
    impactTitle: "MAVVE আর্থিক প্রভাব",
    impactSubtitle: "RTO হ্রাস থেকে আনুমানিক বার্ষিক সঞ্চয়",
    annualSavings: "বার্ষিক সঞ্চয়",
    ordersSalvaged: "রক্ষিত অর্ডার",
    rtoReduction: "RTO হ্রাস",
    languages: "ভাষা",
    totalOrders: "মোট অর্ডার (আজ)",
    avgRto: "গড় RTO হার",
    savedBy: "MAVVE দ্বারা সঞ্চয়",
    activeSessions: "সক্রিয় এজেন্ট সেশন"
  },
  te: {
    impactTitle: "MAVVE ఆర్థిక ప్రభావం",
    impactSubtitle: "RTO తగ్గింపు ద్వారా అంచనా వేసిన వార్షిక పొదుపు",
    annualSavings: "వార్షిక పొదుపు",
    ordersSalvaged: "రక్షించబడిన ఆర్డర్లు",
    rtoReduction: "RTO తగ్గింపు",
    languages: "భాషలు",
    totalOrders: "మొత్తం ఆర్డర్లు (నేడు)",
    avgRto: "సగటు RTO రేటు",
    savedBy: "MAVVE ద్వారా పొదుపు",
    activeSessions: "సక్రియ ఏజెంట్ సెషన్‌లు"
  },
  ta: {
    impactTitle: "MAVVE நிதி தாக்கம்",
    impactSubtitle: "RTO குறைப்பிலிருந்து மதிப்பிடப்பட்ட வருடாந்திர சேமிப்பு",
    annualSavings: "வருடாந்திர சேமிப்பு",
    ordersSalvaged: "காப்பாற்றப்பட்ட ஆர்டர்கள்",
    rtoReduction: "RTO குறைப்பு",
    languages: "மொழிகள்",
    totalOrders: "மொத்த ஆர்டர்கள் (இன்று)",
    avgRto: "சராசரி RTO விகிதம்",
    savedBy: "MAVVE மூலம் சேமிக்கப்பட்டது",
    activeSessions: "செயலில் உள்ள ஏஜென்ட் அமர்வுகள்"
  },
  kn: {
    impactTitle: "MAVVE ಆರ್ಥಿಕ ಪ್ರಭಾವ",
    impactSubtitle: "RTO ಕಡಿತದಿಂದ ಅಂದಾಜು ವಾರ್ಷಿಕ ಉಳಿತಾಯ",
    annualSavings: "ವಾರ್ಷಿಕ ಉಳಿತಾಯ",
    ordersSalvaged: "ಉಳಿಸಲಾದ ಆದೇಶಗಳು",
    rtoReduction: "RTO ಕಡಿತ",
    languages: "ಭಾಷೆಗಳು",
    totalOrders: "ಒಟ್ಟು ಆದೇಶಗಳು (ಇಂದು)",
    avgRto: "ಸರಾಸರಿ RTO ದರ",
    savedBy: "MAVVE ಇಂದ ಉಳಿತಾಯ",
    activeSessions: "ಸಕ್ರಿಯ ಏಜೆಂಟ್ ಸೆಷನ್‌ಗಳು"
  },
  ml: {
    impactTitle: "MAVVE സാമ്പത്തിക സ്വാധീനം",
    impactSubtitle: "RTO കുറയ്ക്കുന്നതിലൂടെ കണക്കാക്കിയ വാർഷിക സമ്പാദ്യം",
    annualSavings: "വാർഷിക സമ്പാദ്യം",
    ordersSalvaged: "സംരക്ഷിച്ച ഓർഡറുകൾ",
    rtoReduction: "RTO കുറവ്",
    languages: "ഭാഷകൾ",
    totalOrders: "മൊത്തം ഓർഡറുകൾ (ഇന്ന്)",
    avgRto: "ശരാശരി RTO നിരക്ക്",
    savedBy: "MAVVE വഴിയുള്ള സമ്പാദ്യം",
    activeSessions: "സജീവ ഏജന്റ് സെഷനുകൾ"
  },
  gu: {
    impactTitle: "MAVVE નાણાકીય અસર",
    impactSubtitle: "RTO ઘટાડાથી અંદાજિત વાર્ષિક બચત",
    annualSavings: "વાર્ષિક બચત",
    ordersSalvaged: "બચાવેલા ઓર્ડર્સ",
    rtoReduction: "RTO માં ઘટાડો",
    languages: "ભાષાઓ",
    totalOrders: "કુલ ઓર્ડર્સ (આજે)",
    avgRto: "સરેરાશ RTO દર",
    savedBy: "MAVVE દ્વારા બચત",
    activeSessions: "સક્રિય એજન્ટ સત્રો"
  },
  pa: {
    impactTitle: "MAVVE ਵਿੱਤੀ ਪ੍ਰਭਾਵ",
    impactSubtitle: "RTO ਕਮੀ ਤੋਂ ਅਨੁਮਾਨਿਤ ਸਾਲਾਨਾ ਬੱਚਤ",
    annualSavings: "ਸਾਲਾਨਾ ਬੱਚਤ",
    ordersSalvaged: "ਬਚਾਏ ਗਏ ਆਰਡਰ",
    rtoReduction: "RTO ਵਿੱਚ ਕਮੀ",
    languages: "ਭਾਸ਼ਾਵਾਂ",
    totalOrders: "ਕੁੱਲ ਆਰਡਰ (ਅੱਜ)",
    avgRto: "ਔਸਤ RTO ਦਰ",
    savedBy: "MAVVE ਦੁਆਰਾ ਬੱਚਤ",
    activeSessions: "ਸਰਗਰਮ ਏਜੰਟ ਸੈਸ਼ਨ"
  },
  or: {
    impactTitle: "MAVVE ଆର୍ଥିକ ପ୍ରଭାବ",
    impactSubtitle: "RTO ହ୍ରାସରୁ ଆନୁମାନିକ ବାର୍ଷିକ ସଞ୍ଚୟ",
    annualSavings: "ବାର୍ଷିକ ସଞ୍ଚୟ",
    ordersSalvaged: "ରକ୍ଷା କରାଯାଇଥିବା ଅର୍ଡର",
    rtoReduction: "RTO ହ୍ରାସ",
    languages: "ଭାଷା",
    totalOrders: "ସମୁଦାୟ ଅର୍ଡର (ଆଜି)",
    avgRto: "ହାରାହାରି RTO ହାର",
    savedBy: "MAVVE ଦ୍ୱାରା ସଞ୍ଚୟ",
    activeSessions: "ସକ୍ରିୟ ଏଜେଣ୍ଟ ଅଧିବେଶନ"
  },
  as: {
    impactTitle: "MAVVE বিত্তীয় প্ৰভাৱ",
    impactSubtitle: "RTO হ্ৰাসৰ পৰা আনুমানিক বাৰ্ষিক সঞ্চয়",
    annualSavings: "বাৰ্ষিক সঞ্চয়",
    ordersSalvaged: "ৰক্ষা কৰা অৰ্ডাৰ",
    rtoReduction: "RTO হ্ৰাস",
    languages: "ভাষা",
    totalOrders: "মুঠ অৰ্ডাৰ (আজি)",
    avgRto: "গড় RTO হাৰ",
    savedBy: "MAVVE দ্বাৰা সঞ্চয়",
    activeSessions: "সক্ৰিয় এজেণ্ট অধিবেশন"
  }
};

export default function Dashboard() {
  const [trendData, setTrendData] = useState(generateTrendData());
  const [areaData, setAreaData] = useState(savingsAreaData);
  const [activeSessions, setActiveSessions] = useState(24);
  const [savings, setSavings] = useState(45290);
  const [hoveredHotspot, setHoveredHotspot] = useState(null);
  
  // Language feature states
  const [showAllLangs, setShowAllLangs] = useState(false);
  const [activeLang, setActiveLang] = useState('en'); // default to english initially
  const [langToast, setLangToast] = useState(null);

  // Intercept Engine states
  const [activeIntercept, setActiveIntercept] = useState(null);
  const [interceptMessages, setInterceptMessages] = useState([]);
  const [isTakeover, setIsTakeover] = useState(false);
  const [adminInput, setAdminInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const timeoutsRef = React.useRef([]);

  // Flip Card state
  const [recentSavings, setRecentSavings] = useState(initialSavings);
  const [isFlipped, setIsFlipped] = useState(false);
  const [selectedSavings, setSelectedSavings] = useState(null);

  // Simulate incoming savings
  useEffect(() => {
    const interval = setInterval(() => {
      const newMocks = [
        { id: `ORD-${Math.floor(Math.random()*900)+100}`, user: 'Neha K.', saved: '₹' + (Math.floor(Math.random()*1500)+100), agent: 'Intent Agent' },
        { id: `ORD-${Math.floor(Math.random()*900)+100}`, user: 'Vikram S.', saved: '₹' + (Math.floor(Math.random()*800)+50), agent: 'Address Agent' },
        { id: `ORD-${Math.floor(Math.random()*900)+100}`, user: 'Ayesha M.', saved: '₹' + (Math.floor(Math.random()*2000)+300), agent: 'Prepaid Agent' },
      ];
      const newSaving = newMocks[Math.floor(Math.random() * newMocks.length)];
      setRecentSavings(prev => [newSaving, ...prev.slice(0, 4)]);
      
      const valSaved = parseInt(newSaving.saved.replace('₹', '').replace(',', ''));
      // Increase total savings counter slightly
      setSavings(prev => prev + valSaved);

      // Sync graphs
      setTrendData(prev => {
        const newData = [...prev];
        newData[newData.length - 1].withMAVVE += (valSaved / 1000);
        return newData;
      });
      setAreaData(prev => {
        const newData = [...prev];
        newData[newData.length - 1].savings += (valSaved / 5000); // Scale for visual bump
        return newData;
      });
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleIntercept = (conv) => {
    // Clear old timeouts
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];

    setActiveIntercept(conv);
    setIsTakeover(false);
    setInterceptMessages([
      { type: 'system', text: `[SYSTEM] Bhashini Live-Sync Established: ${conv.id}` },
      { type: 'agent', text: 'नमस्ते! आपने एक COD ऑर्डर दिया है। क्या आप कैश देने के लिए उपलब्ध होंगे?', trans: 'Hello! You placed a COD order. Will you be available to pay cash?' }
    ]);
    
    // Simulate user typing
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(true);
    }, 2000));
    
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(false);
      setInterceptMessages(prev => [...prev, { type: 'user', text: 'नहीं, मैं ऑफिस में रहूंगा।', trans: 'No, I will be at the office.' }]);
    }, 4500));
    
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(true);
    }, 6000));
    
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(false);
      setInterceptMessages(prev => [...prev, { type: 'agent', text: 'ठीक है। क्या आप इसे प्रीपेड में बदलना चाहेंगे? आपको ₹50 की छूट मिलेगी।', trans: 'Okay. Would you like to convert to prepaid? You get a ₹50 discount.' }]);
    }, 8500));
  };

  const generateMockResponse = (input) => {
    const lower = input.toLowerCase();
    if (lower.includes('hi') || lower.includes('hello') || lower.includes('hey')) {
      return { text: 'नमस्ते! आप मेरी कैसे मदद कर सकते हैं?', trans: 'Hello! How can you help me?' };
    }
    if (lower.includes('cancel') || lower.includes('stop')) {
      return { text: 'ठीक है, कृपया मेरा ऑर्डर रद्द कर दें।', trans: 'Okay, please cancel my order.' };
    }
    if (lower.includes('pay') || lower.includes('upi') || lower.includes('link')) {
      return { text: 'ठीक है, मैं अभी लिंक से भुगतान कर दूंगा।', trans: 'Okay, I will pay via the link now.' };
    }
    if (lower.includes('discount') || lower.includes('offer') || lower.includes('₹')) {
      return { text: 'यह अच्छा ऑफर है, मैं इसके लिए तैयार हूँ।', trans: 'That is a good offer, I am ready for it.' };
    }
    if (lower.includes('address') || lower.includes('location') || lower.includes('where')) {
      return { text: 'मेरा घर मंदिर के पास वाली गली में है।', trans: 'My house is in the lane near the temple.' };
    }
    if (lower.includes('thank')) {
      return { text: 'आपका भी धन्यवाद।', trans: 'Thank you too.' };
    }
    return { text: 'जी, मैं समझ गया। आगे क्या करना है?', trans: 'Yes, I understand. What should I do next?' };
  };

  const handleAdminSend = () => {
    if(!adminInput.trim()) return;
    const currentInput = adminInput;
    setInterceptMessages(prev => [...prev, { type: 'admin', text: currentInput, trans: 'Manual Override Inserted' }]);
    setAdminInput('');
    setIsTyping(false);
    // Clear subsequent automated messages
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];

    const mockResponse = generateMockResponse(currentInput);

    // Simulate customer responding to the admin override
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(true);
    }, 1500));
    
    timeoutsRef.current.push(setTimeout(() => {
      setIsTyping(false);
      setInterceptMessages(prev => [...prev, { type: 'user', text: mockResponse.text, trans: mockResponse.trans }]);
    }, 4000));
  };

  const handleCloseIntercept = () => {
    timeoutsRef.current.forEach(clearTimeout);
    setActiveIntercept(null);
    setIsTakeover(false);
  };

  const t = (key) => {
    return translations[activeLang]?.[key] || translations['en'][key];
  };
  
  const totalOrders = useCountUp(1245);
  const rtoRate = useCountUp(14);
  const displayedSavings = useCountUp(savings);
  const annualSavings = useCountUp(120);
  const ordersSalvaged = useCountUp(156);

  const handleLangClick = (langCode, langName) => {
    setActiveLang(langCode);
    setLangToast(`Bhashini initialized for ${langName}`);
    setTimeout(() => setLangToast(null), 3000);
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveSessions(prev => Math.max(1, prev + Math.floor(Math.random() * 5) - 2));
      setSavings(prev => prev + Math.floor(Math.random() * 500));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-page">

      {/* ── Live Ticker ── */}
      <div className="ticker-strip">
        <div className="ticker-content">
          <div className="ticker-track" style={{display: 'flex'}}>
            {tickerEvents.map((evt, i) => (
              <span key={i}>
                <span className="ticker-dot" style={{backgroundColor: evt.color}}></span>
                {evt.text}
              </span>
            ))}
          </div>
          {/* Duplicate for seamless loop */}
          <div className="ticker-track" style={{display: 'flex'}}>
            {tickerEvents.map((evt, i) => (
              <span key={`dup-${i}`}>
                <span className="ticker-dot" style={{backgroundColor: evt.color}}></span>
                {evt.text}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Financial Impact Hero ── */}
      <div className="impact-hero glass-card glow-border">
        <div className="impact-header">
          <div>
            <h2 className="impact-title">
              <Zap size={22} style={{color: 'var(--accent-primary)'}} />
              {t('impactTitle')}
            </h2>
            <p className="impact-subtitle">{t('impactSubtitle')}</p>
          </div>
          <div className="lang-strip">
            <Languages size={16} style={{color: 'var(--accent-primary)'}} />
            {(showAllLangs ? languages : languages.slice(0, 8)).map(l => (
              <span 
                key={l.code} 
                className={`lang-pill ${activeLang === l.code ? 'active' : ''}`}
                onClick={() => handleLangClick(l.code, l.name)}
                style={{ cursor: 'pointer' }}
              >
                {l.flag} {l.name}
              </span>
            ))}
            {!showAllLangs && (
              <span 
                className="lang-pill" 
                style={{fontWeight: 700, cursor: 'pointer', background: 'rgba(255,255,255,0.05)'}}
                onClick={() => setShowAllLangs(true)}
              >
                +14 more
              </span>
            )}
            {showAllLangs && (
              <span 
                className="lang-pill" 
                style={{fontWeight: 700, cursor: 'pointer', background: 'rgba(255,255,255,0.05)'}}
                onClick={() => setShowAllLangs(false)}
              >
                Show less
              </span>
            )}
          </div>
        </div>
        
        {/* Animated Bhashini Toast */}
        {langToast && (
          <div style={{
            position: 'absolute', top: 16, left: '50%', transform: 'translateX(-50%)',
            background: 'var(--accent-primary)', color: 'white', padding: '8px 16px',
            borderRadius: 'var(--radius-full)', fontSize: '0.85rem', fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: '8px', zIndex: 10,
            boxShadow: '0 4px 12px rgba(var(--accent-primary-rgb), 0.4)',
            animation: 'fadeInUp 0.3s ease-out'
          }}>
            <Radio size={14} className="pulse-icon" /> {langToast}
          </div>
        )}

        <div className="impact-grid">
          <div className="impact-stat">
            <div className="impact-value shine-text">₹{annualSavings} Cr</div>
            <div className="impact-label">{t('annualSavings')}</div>
            <div className="impact-detail">Direct logistics cost reduction</div>
          </div>
          <div className="impact-stat">
            <div className="impact-value shine-text">{ordersSalvaged}M</div>
            <div className="impact-label">{t('ordersSalvaged')}</div>
            <div className="impact-detail">Prevented failed deliveries</div>
          </div>
          <div className="impact-stat">
            <div className="impact-value shine-text">40%</div>
            <div className="impact-label">{t('rtoReduction')}</div>
            <div className="impact-detail">From 24.45% → 14.7% baseline</div>
          </div>
          <div className="impact-stat">
            <div className="impact-value shine-text">22+</div>
            <div className="impact-label">{t('languages')}</div>
            <div className="impact-detail">Bhashini ASR/NMT/TTS powered</div>
          </div>
        </div>
      </div>

      {/* ── Top Stat Cards ── */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-header">
            <span>{t('totalOrders')}</span>
            <Package className="stat-icon" size={32} color="var(--accent-primary)" />
          </div>
          <div className="stat-body">
            <span className="stat-value">{totalOrders.toLocaleString()}</span>
            <span className="stat-trend trend-up"><ArrowUpRight size={16}/> 12%</span>
          </div>
        </div>
        
        <div className="stat-card glass-card">
          <div className="stat-header">
            <span>{t('avgRto')}</span>
            <TrendingDown className="stat-icon" size={32} color="#10b981" />
          </div>
          <div className="stat-body">
            <span className="stat-value">{rtoRate}%</span>
            <span className="stat-trend trend-up" style={{color: '#10b981'}}><ArrowDownRight size={16}/> 4% drop</span>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-header">
            <span>{t('savedBy')}</span>
            <ShieldCheck className="stat-icon" size={32} color="#f59e0b" />
          </div>
          <div className="stat-body">
            <span className="stat-value">₹{displayedSavings.toLocaleString()}</span>
          </div>
        </div>

        <div className="stat-card glass-card">
          <div className="stat-header">
            <span>{t('activeSessions')}</span>
            <Activity className="stat-icon" size={32} color="#ef4444" />
          </div>
          <div className="stat-body">
            <span className="stat-value" style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
              {activeSessions} <span className="pulsing-dot"></span>
            </span>
          </div>
        </div>
      </div>

      {/* ── Middle Row: Charts + India Map ── */}
      <div className="charts-grid-3">
        <div className="chart-card glass-card">
          <div className="chart-header">RTO Rate Trend (30 Days)</div>
          <div className="chart-container" style={{ height: 250, width: '100%' }}>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="day" hide />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc'}} itemStyle={{color: '#f8fafc'}} />
                <Legend />
                <Line type="monotone" dataKey="withoutMAVVE" stroke="#ef4444" strokeWidth={2} name="Baseline RTO %" dot={false} />
                <Line type="monotone" dataKey="withMAVVE" stroke="#10b981" strokeWidth={3} name="MAVVE RTO %" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* India RTO Map */}
        <div className="chart-card glass-card india-map-card">
          <div className="chart-header" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <MapPin size={18} style={{color: 'var(--accent-primary)'}} /> RTO Hotspots — India
          </div>
          <div className="india-map-container">
            <svg viewBox="0 0 100 90" className="india-map-svg">
              {/* Simplified India outline */}
              <path 
                d="M48,8 L55,7 L60,10 L58,15 L62,18 L55,20 L48,18 L45,15 L40,18 L35,22 L30,28 L28,35 L30,42 L32,38 L38,35 L42,38 L45,42 L48,38 L55,35 L62,28 L70,25 L78,22 L85,25 L88,30 L85,35 L80,38 L75,42 L72,48 L68,52 L65,55 L62,60 L58,65 L55,70 L52,75 L48,78 L45,75 L42,70 L38,72 L35,68 L38,62 L42,58 L45,52 L42,48 L38,45 L35,48 L30,52 L28,48 L25,42 L28,38 L25,32 L28,28 L32,25 L38,22 L42,18 L45,12 Z"
                fill="rgba(var(--accent-primary-rgb), 0.05)"
                stroke="rgba(var(--accent-primary-rgb), 0.3)"
                strokeWidth="0.5"
              />
              {/* Hotspot dots */}
              {mapHotspots.map((spot, i) => (
                <g key={i} 
                  onMouseEnter={() => setHoveredHotspot(spot)}
                  onMouseLeave={() => setHoveredHotspot(null)}
                  style={{cursor: 'pointer'}}
                >
                  <circle 
                    cx={spot.x} cy={spot.y} 
                    r={spot.rto > 25 ? 3.5 : spot.rto > 15 ? 2.5 : 1.8}
                    fill={spot.rto > 25 ? '#ef4444' : spot.rto > 15 ? '#f59e0b' : '#10b981'}
                    opacity={0.8}
                  >
                    <animate attributeName="r" 
                      values={`${spot.rto > 25 ? 3.5 : 2.5};${spot.rto > 25 ? 5 : 3.5};${spot.rto > 25 ? 3.5 : 2.5}`} 
                      dur="2s" repeatCount="indefinite" />
                    <animate attributeName="opacity" values="0.8;0.4;0.8" dur="2s" repeatCount="indefinite" />
                  </circle>
                  <circle cx={spot.x} cy={spot.y} r="1" fill="white" opacity="0.9" />
                  <text x={spot.x} y={spot.y - 4} textAnchor="middle" fill="#f8fafc" fontSize="2.5" fontWeight="600">
                    {spot.state}
                  </text>
                </g>
              ))}
            </svg>
            {hoveredHotspot && (
              <div className="map-tooltip">
                <strong>{hoveredHotspot.state}</strong>
                <div>RTO: <span style={{color: hoveredHotspot.rto > 25 ? '#ef4444' : '#f59e0b'}}>{hoveredHotspot.rto}%</span></div>
                <div>Orders: {hoveredHotspot.orders}/day</div>
              </div>
            )}
            <div className="map-legend">
              <span><span className="legend-dot" style={{background: '#ef4444'}}></span>&gt;25%</span>
              <span><span className="legend-dot" style={{background: '#f59e0b'}}></span>15-25%</span>
              <span><span className="legend-dot" style={{background: '#10b981'}}></span>&lt;15%</span>
            </div>
          </div>
        </div>

        <div className="chart-card glass-card">
          <div className="chart-header">Agent Success Breakdown</div>
          <div className="chart-container" style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={agentPerformanceData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc'}} itemStyle={{color: '#f8fafc'}} />
                <Legend />
                <Bar dataKey="success" stackId="a" fill="#10b981" name="Resolved %" radius={[4, 4, 0, 0]} />
                <Bar dataKey="failed" stackId="a" fill="#ef4444" name="Escalated/Cancelled %" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Savings Area Chart ── */}
      <div className="chart-card glass-card" style={{minHeight: '280px'}}>
        <div className="chart-header" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
          <IndianRupee size={18} style={{color: '#10b981'}} /> Monthly Savings Trend (₹ Crore)
        </div>
        <div className="chart-container" style={{ height: 250, width: '100%' }}>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={areaData} margin={{ top: 10, right: 30, bottom: 0, left: 0 }}>

              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} />
              <Tooltip contentStyle={{backgroundColor: 'rgba(15,23,42,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc'}} />
              <Area type="monotone" dataKey="savings" stroke="#10b981" fill="#10b981" fillOpacity={0.3} strokeWidth={2} name="₹ Crore Saved" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Bottom Row ── */}
      <div className="bottom-grid">
        <div className="feed-card glass-card">
          <div className="chart-header" style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Radio size={16} className="pulsing-icon" /> Live Conversations
          </div>
          <div className="feed-list">
            {initialConversations.map((conv, idx) => (
              <div 
                key={idx} 
                className="feed-item" 
                onClick={() => handleIntercept(conv)}
                style={{ cursor: 'pointer' }}
              >
                <div className="feed-icon">
                  <Activity size={20} />
                </div>
                <div className="feed-content">
                  <div className="feed-title">{conv.id} - {conv.user}</div>
                  <div className="feed-desc">Handled by: {conv.agent}</div>
                </div>
                <div>
                  <span className={`badge ${conv.status === 'Active' ? 'badge-success' : conv.status === 'Awaiting' ? 'badge-warning' : 'badge-danger'}`}>
                    {conv.status}
                  </span>
                  <div style={{fontSize: '10px', color: '#94a3b8', textAlign: 'right', marginTop: '4px'}}>{conv.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className={`flip-container ${isFlipped ? 'flipped' : ''}`}>
          <div className="flipper">
            {/* FRONT FACE - The Table */}
            <div className="table-card glass-card front-face">
              <div className="chart-header">
                <span style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <ShieldCheck size={18} style={{color: '#10b981'}} /> Recent Savings 
                </span>
                <span className="live-indicator"><span className="pulsing-dot" style={{width: 8, height: 8}}></span> Live</span>
              </div>
              <div style={{overflowX: 'auto'}}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Customer</th>
                      <th>Agent Used</th>
                      <th>Amount Saved</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentSavings.map((row, idx) => (
                      <tr 
                        key={idx} 
                        className="savings-row" 
                        onClick={() => {
                          setSelectedSavings(row);
                          setIsFlipped(true);
                        }}
                      >
                        <td>{row.id}</td>
                        <td>{row.user}</td>
                        <td><span className="badge badge-info">{row.agent}</span></td>
                        <td style={{color: '#10b981', fontWeight: 'bold'}}>{row.saved}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* BACK FACE - The Forensics Receipt */}
            <div className="table-card glass-card back-face">
              <div className="chart-header" style={{display: 'flex', justifyContent: 'space-between'}}>
                <span style={{display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-primary)'}}>
                  <Cpu size={18} /> AI Forensics Report
                </span>
                <button className="icon-btn" onClick={() => setIsFlipped(false)}>
                  <ArrowLeft size={18} /> Back
                </button>
              </div>
              
              {selectedSavings && (
                <div className="forensics-content">
                  <div className="forensics-title">Order: {selectedSavings.id}</div>
                  
                  <div className="forensics-path">
                    <div className="forensics-node risk">
                      <div className="node-icon"><Activity size={14} /></div>
                      <div className="node-info">
                        <div className="node-label">Risk Assessment</div>
                        <div className="node-val">High RTO Probability (89%)</div>
                      </div>
                    </div>
                    
                    <div className="forensics-line"></div>
                    
                    <div className="forensics-node agent">
                      <div className="node-icon"><Zap size={14} /></div>
                      <div className="node-info">
                        <div className="node-label">Intervention Agent</div>
                        <div className="node-val">{selectedSavings.agent} Deployed</div>
                      </div>
                    </div>

                    <div className="forensics-line"></div>
                    
                    <div className="forensics-node action">
                      <div className="node-icon"><ShieldCheck size={14} /></div>
                      <div className="node-info">
                        <div className="node-label">Action Taken</div>
                        <div className="node-val">Negotiated and secured prepaid payment via UPI.</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="forensics-total">
                    <div className="total-label">Net Savings</div>
                    <div className="total-val">+{selectedSavings.saved}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Live Intercept Modal */}
      {activeIntercept && (
        <div className="intercept-overlay">
          <div className="intercept-modal glass-panel">
            <div className="intercept-header">
              <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                <div className="pulsing-dot"></div>
                <h3 style={{margin: 0, color: 'var(--text-primary)'}}>Live Intercept: {activeIntercept.id}</h3>
              </div>
              <button className="icon-btn" onClick={handleCloseIntercept}><X size={20} /></button>
            </div>
            
            <div className="intercept-body">
              <div className="chat-feed">
                {interceptMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-bubble-wrapper ${msg.type}`}>
                    {msg.type !== 'system' && (
                      <div className="chat-avatar">
                        {msg.type === 'agent' ? <Cpu size={16} /> : msg.type === 'admin' ? <ShieldAlert size={16} /> : <User size={16} />}
                      </div>
                    )}
                    <div className="chat-content">
                      <div className={`chat-bubble ${msg.type}`}>
                        <div className="chat-original">{msg.text}</div>
                        {msg.trans && <div className="chat-translated">{msg.trans}</div>}
                      </div>
                    </div>
                  </div>
                ))}
                {isTyping && (
                  <div className="chat-bubble-wrapper agent">
                    <div className="chat-avatar"><User size={16} /></div>
                    <div className="chat-bubble agent typing-indicator">
                      <span>.</span><span>.</span><span>.</span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="intercept-controls">
                {!isTakeover ? (
                  <button className="takeover-btn" onClick={() => setIsTakeover(true)}>
                    <ShieldAlert size={18} /> Take Over Conversation
                  </button>
                ) : (
                  <div className="takeover-active-panel">
                    <div className="takeover-warning">
                      <ShieldAlert size={14} /> AI Paused. You are now speaking directly to the customer.
                    </div>
                    <div className="admin-input-group">
                      <input 
                        type="text" 
                        placeholder="Type a message to the customer..."
                        value={adminInput}
                        onChange={e => setAdminInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleAdminSend()}
                        autoFocus
                      />
                      <button onClick={handleAdminSend} className="send-btn"><Send size={18} /></button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
