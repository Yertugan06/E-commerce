interface QuantitySelectorProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
}

export function QuantitySelector({ value, onChange, min = 1 }: QuantitySelectorProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <button type="button" onClick={() => onChange(Math.max(min, value - 1))} disabled={value <= min}>
        -
      </button>
      <span>{value}</span>
      <button type="button" onClick={() => onChange(value + 1)}>
        +
      </button>
    </div>
  );
}
