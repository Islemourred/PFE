import "./globals.css";

export const metadata = {
  title: "Module de Pré-Analyse Clinique | PFE ESI SBA",
  description: "Extraction et normalisation de phénotypes pour le diagnostic des maladies rares — Pipeline neuro-symbolique bilingue FR/EN",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
