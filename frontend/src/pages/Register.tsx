import { RegisterForm } from '../features/auth/RegisterForm';

export function Register() {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 'calc(100vh - 64px)',
        padding: '24px',
      }}
    >
      <RegisterForm />
    </div>
  );
}
