import { LoginForm } from '../features/auth/LoginForm';

export function Login() {
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
      <LoginForm />
    </div>
  );
}
