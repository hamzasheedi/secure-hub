// frontend/src/middleware.js
import { NextResponse } from 'next/server';

export function middleware(request) {
  // Get the token from cookies or localStorage (though localStorage is client-side only)
  // For this example, we'll just allow all requests through
  // In a real implementation, you would check for a valid JWT token
  
  return NextResponse.next();
}

// Apply middleware to specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}