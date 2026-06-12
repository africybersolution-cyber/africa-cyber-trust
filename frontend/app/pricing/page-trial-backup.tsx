'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Country {
  code: string;
  name: string;
  currency: string;
  personal: string;
  business: string;
  operators: string[];
}

export default function PricingPage() {
  const router = useRouter();
  const [countries, setCountries] = useState<Country[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>('RW');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const res = await fetch('/api/payments/pricing');
        if (res.ok) {
          const data = await res.json();
          setCountries(data.countries);
        }
      } catch (error) {
        console.error('Failed to fetch pricing:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPricing();
  }, []);

  const currentCountry = countries.find(c => c.code === selectedCountry) || countries[0];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-700 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading pricing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4" style={{ color: '#0047AB' }}>
              Simple, Transparent Pricing
            </h1>
            <p className="text-xl text-gray-600 mb-6">
              Choose your country to see pricing in your local currency
            </p>

            <div className="max-w-md mx-auto">
              <select
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none"
              >
                {countries.map((country) => (
                  <option key={country.code} value={country.code}>
                    {country.name} ({country.currency})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-12 text-center">
            <div className="inline-block px-6 py-3 rounded-full text-lg font-semibold text-green-700 bg-green-100">
              14-Day Free Trial • No Credit Card Required
            </div>
          </div>

          {currentCountry && (
            <div className="grid md:grid-cols-2 gap-8 mb-12">
              <div className="bg-white rounded-2xl shadow-xl p-8 border-2 border-gray-200">
                <h3 className="text-2xl font-bold mb-2" style={{ color: '#0047AB' }}>Personal</h3>
                <div className="text-5xl font-bold mb-4" style={{ color: '#0047AB' }}>
                  {parseInt(currentCountry.personal).toLocaleString()} {currentCountry.currency}
                  <div className="text-lg font-normal text-gray-600">/month</div>
                </div>
                <button
                  onClick={() => router.push('/get-started')}
                  className="w-full py-4 rounded-xl font-bold text-white shadow-lg"
                  style={{ background: 'linear-gradient(135deg, #0047AB 0%, #1E90FF 100%)' }}
                >
                  Start Free Trial
                </button>
              </div>

              <div className="bg-white rounded-2xl shadow-xl p-8 border-2 border-green-500">
                <h3 className="text-2xl font-bold mb-2 text-green-600">Business</h3>
                <div className="text-5xl font-bold mb-4 text-green-600">
                  {parseInt(currentCountry.business).toLocaleString()} {currentCountry.currency}
                  <div className="text-lg font-normal text-gray-600">/month</div>
                </div>
                <button
                  onClick={() => router.push('/get-started')}
                  className="w-full py-4 rounded-xl font-bold text-white shadow-lg"
                  style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }}
                >
                  Start Free Trial
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
