import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, Eye, EyeOff, ArrowRight } from 'lucide-react';

// Flying Bird Component
const FlyingBird = ({ delay, duration, yStart, scale }: { delay: number; duration: number; yStart: number; scale: number }) => {
  return (
    <motion.svg
      className="absolute"
      initial={{ x: -100, y: yStart, opacity: 0 }}
      animate={{
        x: ['0vw', '120vw'],
        y: [yStart, yStart - 30, yStart + 20, yStart - 10, yStart],
        opacity: [0, 1, 1, 1, 0],
      }}
      transition={{
        duration: duration,
        delay: delay,
        repeat: Infinity,
        ease: 'linear',
      }}
      width="40"
      height="40"
      viewBox="0 0 40 40"
      style={{ scale }}
    >
      <motion.path
        d="M5 20 Q15 10 20 20 Q25 10 35 20"
        stroke="#2d1b4e"
        strokeWidth="2"
        fill="none"
        animate={{
          d: [
            "M5 20 Q15 10 20 20 Q25 10 35 20",
            "M5 20 Q15 25 20 20 Q25 25 35 20",
            "M5 20 Q15 10 20 20 Q25 10 35 20",
          ],
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </motion.svg>
  );
};

// Animated Mountain Layer
const MountainLayer = ({ 
  color, 
  height, 
  delay,
  points 
}: { 
  color: string; 
  height: string; 
  delay: number;
  points: string;
}) => {
  return (
    <motion.div
      className={`absolute bottom-0 w-full ${height}`}
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 1.5, delay, ease: 'easeOut' }}
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 1440 320"
        preserveAspectRatio="none"
      >
        <motion.path
          fill={color}
          d={points}
          animate={{
            d: [
              points,
              points.replace(/Q\d+ \d+/g, (match) => {
                const nums = match.match(/\d+/g);
                if (nums) {
                  return `Q${nums[0]} ${parseInt(nums[1]) + Math.sin(Date.now() / 1000) * 5}`;
                }
                return match;
              }),
            ],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'easeInOut',
          }}
        />
      </svg>
    </motion.div>
  );
};

// Floating Particle
const Particle = ({ delay, x, y }: { delay: number; x: string; y: string }) => (
  <motion.div
    className="absolute w-1 h-1 bg-white rounded-full opacity-40"
    style={{ left: x, top: y }}
    animate={{
      y: [0, -30, 0],
      opacity: [0.2, 0.6, 0.2],
      scale: [1, 1.5, 1],
    }}
    transition={{
      duration: 4,
      delay,
      repeat: Infinity,
      ease: 'easeInOut',
    }}
  />
);

function App() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
  });
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-b from-[#ffd1b3] via-[#ffb3ba] to-[#d4a5d4]">
      {/* Animated Sun */}
      <motion.div
        className="absolute top-8 right-12 w-24 h-24 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 50%, transparent 70%)',
          boxShadow: '0 0 60px 20px rgba(255, 255, 255, 0.3)',
        }}
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.8, 1, 0.8],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />

      {/* Flying Birds */}
      <FlyingBird delay={0} duration={15} yStart={80} scale={1} />
      <FlyingBird delay={3} duration={18} yStart={120} scale={0.8} />
      <FlyingBird delay={6} duration={16} yStart={60} scale={0.9} />
      <FlyingBird delay={9} duration={20} yStart={100} scale={0.7} />
      <FlyingBird delay={12} duration={17} yStart={140} scale={0.85} />
      <FlyingBird delay={2} duration={19} yStart={90} scale={0.75} />

      {/* Floating Particles */}
      <Particle delay={0} x="10%" y="20%" />
      <Particle delay={1} x="25%" y="35%" />
      <Particle delay={2} x="70%" y="25%" />
      <Particle delay={1.5} x="85%" y="40%" />
      <Particle delay={0.5} x="50%" y="15%" />
      <Particle delay={2.5} x="15%" y="50%" />
      <Particle delay={3} x="90%" y="30%" />

      {/* Mountain Layers */}
      <MountainLayer
        color="#9b7cb6"
        height="h-64"
        delay={0.3}
        points="M0,200 Q150,100 300,180 T600,150 T900,190 T1200,140 T1440,180 V320 H0 Z"
      />
      <MountainLayer
        color="#b8a1c9"
        height="h-48"
        delay={0.5}
        points="M0,250 Q200,150 400,220 T800,180 T1200,200 T1440,170 V320 H0 Z"
      />
      <MountainLayer
        color="#d4b5c4"
        height="h-32"
        delay={0.7}
        points="M0,280 Q180,200 360,260 T720,220 T1080,250 T1440,210 V320 H0 Z"
      />

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="w-full max-w-md"
        >
          {/* Glass Card */}
          <motion.div
            className="relative backdrop-blur-xl bg-white/20 rounded-3xl p-8 shadow-2xl border border-white/30"
            style={{
              boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
            }}
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Title */}
            <motion.h1
              className="text-3xl font-bold text-white text-center mb-8 tracking-wide"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              style={{ textShadow: '0 2px 10px rgba(0,0,0,0.1)' }}
            >
              {isLogin ? 'Login Form' : 'Sign Up'}
            </motion.h1>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Name Field - Only for Sign Up */}
              <AnimatePresence mode="wait">
                {!isLogin && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="relative">
                      <motion.div
                        className="absolute left-0 bottom-3 text-white/70"
                        animate={{ scale: focusedField === 'name' ? 1.1 : 1 }}
                      >
                        <User size={20} />
                      </motion.div>
                      <input
                        type="text"
                        placeholder="Enter your name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        onFocus={() => setFocusedField('name')}
                        onBlur={() => setFocusedField(null)}
                        className="w-full bg-transparent border-b-2 border-white/40 focus:border-white text-white placeholder-white/70 py-2 pl-8 pr-4 outline-none transition-all duration-300"
                      />
                      <motion.div
                        className="absolute bottom-0 left-0 h-0.5 bg-white"
                        initial={{ width: '0%' }}
                        animate={{ width: focusedField === 'name' ? '100%' : '0%' }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Email Field */}
              <motion.div
                className="relative"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
              >
                <motion.div
                  className="absolute left-0 bottom-3 text-white/70"
                  animate={{ scale: focusedField === 'email' ? 1.1 : 1 }}
                >
                  <Mail size={20} />
                </motion.div>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                  className="w-full bg-transparent border-b-2 border-white/40 focus:border-white text-white placeholder-white/70 py-2 pl-8 pr-4 outline-none transition-all duration-300"
                />
                <motion.div
                  className="absolute bottom-0 left-0 h-0.5 bg-white"
                  initial={{ width: '0%' }}
                  animate={{ width: focusedField === 'email' ? '100%' : '0%' }}
                  transition={{ duration: 0.3 }}
                />
              </motion.div>

              {/* Password Field */}
              <motion.div
                className="relative"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <motion.div
                  className="absolute left-0 bottom-3 text-white/70"
                  animate={{ scale: focusedField === 'password' ? 1.1 : 1 }}
                >
                  <Lock size={20} />
                </motion.div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                  className="w-full bg-transparent border-b-2 border-white/40 focus:border-white text-white placeholder-white/70 py-2 pl-8 pr-10 outline-none transition-all duration-300"
                />
                <motion.div
                  className="absolute bottom-0 left-0 h-0.5 bg-white"
                  initial={{ width: '0%' }}
                  animate={{ width: focusedField === 'password' ? '100%' : '0%' }}
                  transition={{ duration: 0.3 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-0 bottom-3 text-white/70 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </motion.div>

              {/* Remember Me & Forgot Password - Only for Login */}
              {isLogin && (
                <motion.div
                  className="flex items-center justify-between text-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 }}
                >
                  <label className="flex items-center text-white/90 cursor-pointer group">
                    <input type="checkbox" className="mr-2 accent-purple-600" />
                    <span className="group-hover:text-white transition-colors">Remember me</span>
                  </label>
                  <motion.a
                    href="#"
                    className="text-white/90 hover:text-white transition-colors"
                    whileHover={{ scale: 1.05 }}
                  >
                    Forgot password?
                  </motion.a>
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                className="w-full bg-[#2d1b4e] text-white font-semibold py-4 rounded-full mt-6 relative overflow-hidden group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <motion.span
                  className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                />
                <span className="relative flex items-center justify-center gap-2">
                  {isLogin ? 'Log In' : 'Sign Up'}
                  <motion.div
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <ArrowRight size={18} />
                  </motion.div>
                </span>
              </motion.button>
            </form>

            {/* Toggle Link */}
            <motion.div
              className="text-center mt-6 text-white/90"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9 }}
            >
              <span>
                {isLogin ? "Don't have an account? " : "Already have an account? "}
              </span>
              <motion.button
                onClick={() => setIsLogin(!isLogin)}
                className="font-semibold text-white hover:underline"
                whileHover={{ scale: 1.05 }}
              >
                {isLogin ? 'Register' : 'Log In'}
              </motion.button>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Gradient Overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/10 via-transparent to-transparent pointer-events-none" />
    </div>
  );
}

export default App;