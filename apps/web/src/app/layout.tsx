import type { Metadata, Viewport } from 'next'
import { Syne, Nunito } from 'next/font/google'
import './globals.css'

const syne = Syne({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-syne',
  display: 'swap',
})

const nunito = Nunito({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-nunito',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'Top5 Fantasy',
    template: '%s — Top5 Fantasy',
  },
  description:
    'Season-long fantasy football across the Premier League, La Liga, Bundesliga, Serie A, and Ligue 1.',
  metadataBase: new URL(process.env.APP_URL ?? 'http://localhost:3000'),
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#F7F4EE',
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${syne.variable} ${nunito.variable}`}>
      <body className="font-sans" suppressHydrationWarning>{children}</body>
    </html>
  )
}
