// app/layout.tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Búsqueda de Talento',
  description: 'Sistema de búsqueda de candidatos con IA',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}