export default function Footer() {
  return (
    <footer className="border-t border-cozy-border mt-16 py-6 text-center text-sm text-neutral-400 bg-cozy-card">
      <span className="font-semibold text-primary-600">TuniTech Advisor</span>
      {' '}© {new Date().getFullYear()} — Smart Smartphone Advisor for the Tunisian Market
    </footer>
  );
}
