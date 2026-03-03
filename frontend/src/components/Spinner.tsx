import { Loader2 } from 'lucide-react';

interface Props {
  text?: string;
}

export default function Spinner({ text = 'Loading…' }: Props) {
  return (
    <div className="flex flex-col items-center gap-3 py-16 text-gray-500">
      <Loader2 className="animate-spin text-primary-500" size={36} />
      <p className="text-sm">{text}</p>
    </div>
  );
}
