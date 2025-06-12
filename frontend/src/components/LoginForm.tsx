import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { authService } from '@/services/auth';
import { getErrorMessage } from '@/services/axios';

// Form validation schemas
const loginSchema = z.object({
  username_or_email: z.string().min(1, 'Username or email is required'),
  password: z.string().min(1, 'Password is required'),
});

const otpSchema = z.object({
  otp: z.string().length(6, 'OTP must be 6 digits'),
});

type LoginStage = 'credentials' | 'otp';

export function LoginForm() {
  const navigate = useNavigate();
  const [stage, setStage] = useState<LoginStage>('credentials');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Handle credentials submission
  const handleCredentialsSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      username_or_email: formData.get('username_or_email') as string,
      password: formData.get('password') as string,
    };

    try {
      // Validate input
      loginSchema.parse(data);

      // Attempt login
      await authService.login(data);
      setStage('otp');
    } catch (error) {
      setError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  // Handle OTP submission
  const handleOTPSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const data = {
      user_id: authService.getUserId() || '',
      otp: formData.get('otp') as string,
    };

    try {
      // Validate input
      otpSchema.parse(data);

      // Verify OTP
      await authService.verify2FA(data);
      navigate('/dashboard');
    } catch (error) {
      setError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2 text-center">
        <h1 className="text-2xl font-bold">
          {stage === 'credentials' ? 'Login' : 'Enter OTP'}
        </h1>
        <p className="text-muted-foreground">
          {stage === 'credentials'
            ? 'Enter your credentials to continue'
            : 'Enter the 6-digit code sent to your email'}
        </p>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive text-sm p-3 rounded-md">
          {error}
        </div>
      )}

      {stage === 'credentials' ? (
        <form onSubmit={handleCredentialsSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="username_or_email"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Username or Email
            </label>
            <input
              id="username_or_email"
              name="username_or_email"
              type="text"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Enter your username or email"
              disabled={isLoading}
            />
          </div>
          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Continue'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleOTPSubmit} className="space-y-4">
          <div className="space-y-2">
            <label
              htmlFor="otp"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              One-Time Password
            </label>
            <input
              id="otp"
              name="otp"
              type="text"
              maxLength={6}
              pattern="[0-9]*"
              inputMode="numeric"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="Enter 6-digit code"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground ring-offset-background transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? 'Verifying...' : 'Verify OTP'}
          </button>
        </form>
      )}
    </div>
  );
} 