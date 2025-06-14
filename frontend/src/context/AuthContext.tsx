import { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentMerchantDashboard, login as apiLogin, logout as apiLogout } from '@/api/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));

  useEffect(() => {
    if (token) {
      getCurrentMerchantDashboard()
        .then((res) => setUser(res.data))
        .catch(() => {
          apiLogout();
          setUser(null);
        });
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    const data = await apiLogin(username, password);
    setToken(data.token);
    const profile = await getCurrentMerchantDashboard();
    setUser(profile.data);
  };

  const logout = () => {
    apiLogout();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
