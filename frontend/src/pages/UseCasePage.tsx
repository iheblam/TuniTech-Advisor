import { useState } from 'react';
import { Target, Gamepad2, Camera, Battery, GraduationCap, Briefcase, Wifi, ChevronRight } from 'lucide-react';
import { getRecommendations } from '../api/client';
import type { SmartphoneDetail, RecommendationRequest } from '../types';
import PhoneCard from '../components/PhoneCard';
import Spinner from '../components/Spinner';

interface UseCase {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  params: Partial<RecommendationRequest>;
}

const USE_CASES: UseCase[] = [
  {
    id: 'gaming',
    label: 'Gaming Beast',
    description: 'High performance, large battery, 8+ GB RAM for smooth gameplay',
    icon: <Gamepad2 size={28} />,
    color: 'bg-purple-100 text-purple-700',
    params: { min_ram: 8, min_battery: 4500, budget_min: 600, budget_max: 3000, limit: 20 },
  },
  {
    id: 'photography',
    label: 'Photography Pro',
    description: 'Best cameras for stunning shots, high-res rear and front lenses',
    icon: <Camera size={28} />,
    color: 'bg-pink-100 text-pink-700',
    params: { min_camera: 48, min_ram: 6, budget_min: 800, budget_max: 4000, limit: 20 },
  },
  {
    id: 'battery',
    label: 'Battery Champion',
    description: 'Massive battery for all-day use, never run out of charge',
    icon: <Battery size={28} />,
    color: 'bg-green-100 text-green-700',
    params: { min_battery: 5000, budget_min: 0, budget_max: 2000, limit: 20 },
  },
  {
    id: 'student',
    label: 'Student Budget',
    description: 'Affordable phones with solid specs — best value for money',
    icon: <GraduationCap size={28} />,
    color: 'bg-blue-100 text-blue-700',
    params: { budget_min: 0, budget_max: 700, min_ram: 4, min_storage: 64, limit: 20 },
  },
  {
    id: 'work',
    label: 'Work Power User',
    description: 'Large storage, reliable performance, all-day productivity',
    icon: <Briefcase size={28} />,
    color: 'bg-amber-100 text-amber-700',
    params: { min_ram: 8, min_storage: 128, budget_min: 800, budget_max: 3500, limit: 20 },
  },
  {
    id: '5g',
    label: 'Best 5G Phone',
    description: 'Future-proof with 5G connectivity at the best price',
    icon: <Wifi size={28} />,
    color: 'bg-cyan-100 text-cyan-700',
    params: { requires_5g: true, budget_min: 0, budget_max: 4000, limit: 20 },
  },
];

export default function UseCasePage() {
  const [selected, setSelected]   = useState<UseCase | null>(null);
  const [results, setResults]     = useState<SmartphoneDetail[]>([]);
  const [total, setTotal]         = useState<number | null>(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState('');

  const handleSelect = async (uc: UseCase) => {
    setSelected(uc);
    setLoading(true);
    setError('');
    setResults([]);
    try {
      const req: RecommendationRequest = {
        budget_min: 0,
        budget_max: 99999,
        ...uc.params,
      };
      const data = await getRecommendations(req);
      setResults(data.recommendations ?? []);
      setTotal(data.total_found ?? 0);
    } catch {
      setError('Could not load recommendations. Is the API running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-primary-100 text-primary-700">
            <Target size={22} />
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900">Find Your Perfect Phone</h1>
        </div>
        <p className="text-gray-500 max-w-xl">
          Tell us how you use your phone — we'll match you with the best options from Tunisian stores.
        </p>
      </div>

      {/* Use case grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        {USE_CASES.map((uc) => (
          <button
            key={uc.id}
            onClick={() => handleSelect(uc)}
            className={`text-left p-5 rounded-2xl border transition-all hover:shadow-md hover:-translate-y-0.5 ${
              selected?.id === uc.id
                ? 'border-primary-400 shadow-md ring-2 ring-primary-100'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className={`inline-flex p-3 rounded-xl mb-3 ${uc.color}`}>
              {uc.icon}
            </div>
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-gray-900">{uc.label}</h3>
              <ChevronRight size={16} className={`text-gray-300 transition-colors ${selected?.id === uc.id ? 'text-primary-500' : ''}`} />
            </div>
            <p className="text-sm text-gray-500 mt-1 leading-snug">{uc.description}</p>
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex justify-center py-16">
          <Spinner text={`Finding best ${selected?.label} phones…`} />
        </div>
      )}

      {/* Error */}
      {error && (
        <p className="text-red-600 text-sm mb-4 bg-red-50 border border-red-200 rounded-lg px-3 py-2">{error}</p>
      )}

      {/* Results */}
      {!loading && results.length > 0 && selected && (
        <div>
          <div className="flex items-center gap-3 mb-5">
            <div className={`inline-flex p-2 rounded-xl ${selected.color}`}>
              {selected.icon}
            </div>
            <div>
              <h2 className="font-bold text-gray-900 text-lg">
                {selected.label} Recommendations
              </h2>
              <p className="text-sm text-gray-400">
                {total} phones found matching your profile
              </p>
            </div>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {results.map((p, i) => <PhoneCard key={i} phone={p} />)}
          </div>
        </div>
      )}

      {!loading && !selected && (
        <p className="text-center text-gray-400 py-8">Select a use case above to see recommendations →</p>
      )}
    </div>
  );
}
