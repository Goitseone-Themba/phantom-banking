import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface KYCFormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  nationality: string;
  document_type: 'passport' | 'id_card' | 'driving_license';
  document_number: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
}

interface KYCStatus {
  kyc_status: string;
  is_verified: boolean;
  verification_level: string;
  created_at?: string;
  verified_at?: string;
  expires_at?: string;
  wallet_info?: {
    wallet_type: string;
    balance: string;
    can_upgrade: boolean;
  };
}

const KYCVerification: React.FC = () => {
  const [formData, setFormData] = useState<KYCFormData>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    nationality: 'BW',
    document_type: 'passport',
    document_number: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state_province: '',
    postal_code: '',
    country: 'BW'
  });

  const [kycStatus, setKycStatus] = useState<KYCStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'status' | 'form' | 'processing'>('status');

  useEffect(() => {
    checkKYCStatus();
  }, []);

  const checkKYCStatus = async () => {
    try {
      const response = await axios.get('/api/kyc/summary/');
      setKycStatus(response.data);
      
      if (response.data.kyc_status === 'not_started') {
        setStep('form');
      } else if (response.data.kyc_status === 'in_progress') {
        setStep('processing');
      } else {
        setStep('status');
      }
    } catch (error) {
      console.error('Failed to check KYC status:', error);
      setError('Failed to load KYC status');
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const startKYCVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/kyc/records/start_verification/', formData);
      
      if (response.data.session_url) {
        // Redirect to Veriff verification
        window.location.href = response.data.session_url;
      } else {
        setError('Failed to start verification session');
      }
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to start verification');
    } finally {
      setLoading(false);
    }
  };

  const renderStatusView = () => (
    <div className="kyc-status">
      <h2>KYC Verification Status</h2>
      
      {kycStatus?.is_verified ? (
        <div className="status-verified">
          <div className="status-icon">✅</div>
          <h3>Verification Complete</h3>
          <p>Your identity has been successfully verified.</p>
          
          {kycStatus.wallet_info && (
            <div className="wallet-info">
              <h4>Wallet Information</h4>
              <p>Type: {kycStatus.wallet_info.wallet_type}</p>
              <p>Balance: ${kycStatus.wallet_info.balance}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="status-pending">
          <div className="status-icon">⏳</div>
          <h3>Verification {kycStatus?.kyc_status}</h3>
          <p>Your verification is currently being processed.</p>
          <button onClick={checkKYCStatus} className="btn-refresh">
            Refresh Status
          </button>
        </div>
      )}
    </div>
  );

  const renderFormView = () => (
    <div className="kyc-form">
      <h2>Identity Verification</h2>
      <p>Please provide your information to start the verification process.</p>
      
      <form onSubmit={startKYCVerification}>
        <div className="form-section">
          <h3>Personal Information</h3>
          
          <div className="form-group">
            <label htmlFor="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="date_of_birth">Date of Birth *</label>
            <input
              type="date"
              id="date_of_birth"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="nationality">Nationality *</label>
            <select
              id="nationality"
              name="nationality"
              value={formData.nationality}
              onChange={handleInputChange}
              required
            >
              <option value="BW">Botswana</option>
              <option value="ZA">South Africa</option>
              <option value="US">United States</option>
              <option value="GB">United Kingdom</option>
              {/* Add more countries as needed */}
            </select>
          </div>
        </div>

        <div className="form-section">
          <h3>Document Information</h3>
          
          <div className="form-group">
            <label htmlFor="document_type">Document Type *</label>
            <select
              id="document_type"
              name="document_type"
              value={formData.document_type}
              onChange={handleInputChange}
              required
            >
              <option value="passport">Passport</option>
              <option value="id_card">National ID Card</option>
              <option value="driving_license">Driving License</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="document_number">Document Number *</label>
            <input
              type="text"
              id="document_number"
              name="document_number"
              value={formData.document_number}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Address Information</h3>
          
          <div className="form-group">
            <label htmlFor="address_line_1">Address Line 1 *</label>
            <input
              type="text"
              id="address_line_1"
              name="address_line_1"
              value={formData.address_line_1}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="address_line_2">Address Line 2</label>
            <input
              type="text"
              id="address_line_2"
              name="address_line_2"
              value={formData.address_line_2}
              onChange={handleInputChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="city">City *</label>
            <input
              type="text"
              id="city"
              name="city"
              value={formData.city}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="state_province">State/Province *</label>
            <input
              type="text"
              id="state_province"
              name="state_province"
              value={formData.state_province}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="postal_code">Postal Code *</label>
            <input
              type="text"
              id="postal_code"
              name="postal_code"
              value={formData.postal_code}
              onChange={handleInputChange}
              required
            />
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Starting Verification...' : 'Start Verification'}
        </button>
      </form>
    </div>
  );

  const renderProcessingView = () => (
    <div className="kyc-processing">
      <div className="processing-animation">⏳</div>
      <h2>Verification in Progress</h2>
      <p>Your verification is being processed. This may take a few minutes.</p>
      <button onClick={checkKYCStatus} className="btn-refresh">
        Check Status
      </button>
    </div>
  );

  return (
    <div className="kyc-verification">
      {step === 'status' && renderStatusView()}
      {step === 'form' && renderFormView()}
      {step === 'processing' && renderProcessingView()}
    </div>
  );
};

export default KYCVerification;