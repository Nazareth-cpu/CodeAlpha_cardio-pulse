import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Activity, ArrowRight, HeartPulse, LogOut, Menu, User as UserIcon, X } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../ui/Button';

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { currentUser, signOut } = useAuth();
  const { success, error: toastError } = useToast();
  const location = useLocation();
  const navigate = useNavigate();

  const handleSignOut = async () => {
    try {
      await signOut();
      success('Signed out', 'You have been securely signed out.');
      navigate('/login');
    } catch {
      toastError('Sign out error', 'Failed to sign out. Please try again.');
    }
  };

  const navLinks = [
    { label: 'Home', href: '/', isHash: false },
    { label: 'How It Works', href: '/#how-it-works', isHash: true },
    { label: 'About Model', href: '/about-model', isHash: false },
    { label: 'Features', href: '/#product-preview', isHash: true },
    { label: 'Contact', href: '#contact', isHash: true },
    ...(currentUser
      ? [
          { label: 'Dashboard', href: '/dashboard', isHash: false },
          { label: 'Assessment', href: '/assessment', isHash: false },
          { label: 'History', href: '/history', isHash: false },
        ]
      : []),
  ];

  const isActive = (path: string, isHash: boolean) => {
    if (isHash) return false;
    if (path === '/') return location.pathname === '/' && !location.hash;
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 backdrop-blur-md border-b border-[#E2ECE8]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        {/* Brand: HeartCare AI + Educational ML App */}
        <Link
          to="/"
          className="flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#087F5B] rounded-xl p-1 -ml-1"
        >
          <div className="relative w-9 h-9 rounded-xl bg-linear-to-br from-[#087F5B] to-[#14B8A6] text-white flex items-center justify-center shadow-xs border border-[#087F5B]/30">
            <HeartPulse className="w-5 h-5 stroke-[2.4]" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[#F4B942] border-2 border-white" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-base text-[#087F5B] tracking-tight leading-tight">
              HeartCare AI
            </span>
            <span className="text-[10px] text-[#65756F] font-semibold -mt-0.5">
              Educational ML App
            </span>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6 lg:gap-8">
          {navLinks.map((link) => {
            const active = isActive(link.href, link.isHash);
            const content = (
              <span
                className={`text-xs font-semibold tracking-tight transition-all duration-150 py-1 ${
                  active
                    ? 'text-[#087F5B] font-bold border-b-2 border-[#F4B942]'
                    : 'text-[#65756F] hover:text-[#087F5B] hover:border-b-2 hover:border-[#F4B942]/60'
                }`}
              >
                {link.label}
              </span>
            );

            return link.href.startsWith('#') || link.href.includes('#') ? (
              <a key={link.label} href={link.href} className="focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#087F5B] rounded px-1">
                {content}
              </a>
            ) : (
              <Link key={link.label} to={link.href} className="focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#087F5B] rounded px-1">
                {content}
              </Link>
            );
          })}
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-3">
          {currentUser ? (
            <div className="flex items-center gap-3">
              <Link
                to="/profile"
                className="flex items-center gap-2 py-1.5 px-3 rounded-lg bg-[#F6FAF8] border border-[#E2ECE8] hover:bg-slate-100 transition-colors text-xs text-[#12231E]"
              >
                <UserIcon className="w-3.5 h-3.5 text-[#087F5B]" />
                <span className="font-semibold max-w-[130px] truncate">
                  {currentUser.email || 'Clinician'}
                </span>
              </Link>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<LogOut className="w-3.5 h-3.5 text-[#087F5B]" />}
                onClick={handleSignOut}
              >
                Sign Out
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2.5">
              <Link to="/login">
                <Button size="sm" variant="ghost" className="font-semibold text-xs text-[#12231E]">
                  Sign In
                </Button>
              </Link>
              <Link to="/signup">
                <Button
                  size="sm"
                  variant="amber"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5 text-[#12231E]" />}
                  className="font-bold text-xs"
                >
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile menu trigger */}
        <div className="flex md:hidden">
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
            className="p-2 text-[#12231E] hover:text-[#087F5B] rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#087F5B]"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-[#E2ECE8] bg-white px-5 pt-3 pb-6 space-y-4 shadow-lg animate-in slide-in-from-top-2">
          <nav className="flex flex-col space-y-2">
            {navLinks.map((link) => {
              const active = isActive(link.href, link.isHash);
              const className = `px-3 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-between ${
                active
                  ? 'bg-[#E6F3EF] text-[#087F5B] border-l-4 border-[#F4B942]'
                  : 'text-[#65756F] hover:text-[#12231E] hover:bg-[#F6FAF8]'
              }`;

              return link.href.startsWith('#') || link.href.includes('#') ? (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={className}
                >
                  <span>{link.label}</span>
                </a>
              ) : (
                <Link
                  key={link.label}
                  to={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={className}
                >
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="pt-3 border-t border-[#E2ECE8] flex flex-col gap-2.5">
            {currentUser ? (
              <>
                <Link
                  to="/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-3 py-2 text-xs text-[#65756F] font-medium"
                >
                  Signed in as <span className="font-bold text-[#12231E]">{currentUser.email}</span>
                </Link>
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<LogOut className="w-4 h-4 text-[#087F5B]" />}
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleSignOut();
                  }}
                  className="w-full"
                >
                  Sign Out
                </Button>
              </>
            ) : (
              <div className="grid grid-cols-2 gap-2.5">
                <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="outline" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                  <Button size="sm" variant="amber" className="w-full">
                    Get Started
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
