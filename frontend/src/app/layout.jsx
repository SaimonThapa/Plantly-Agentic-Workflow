import "./globals.css";

export const metadata = {
  title: "Plantly — From soil to a growing plan",
  description:
    "Research-backed seasonal planning in development for home gardeners and small growers.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}