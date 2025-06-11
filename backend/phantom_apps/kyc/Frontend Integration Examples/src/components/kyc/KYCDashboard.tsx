import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface KYCRecord {
  id: string;
  user_email: string;
  status: string;
  verification_level: string;
  first_name: string;
  last_name: string;
  created_at: string;
  verified_at?: string;
  is_verified: boolean;
}

interface KYCEvent {
  id: string;
  event_type: string;
  description: string;
  created_at: string;
  created_by_email?: string;
}

const KYCDashboard: React.FC = () => {
  const [kycRecords, setKycRecords] = useState<KYCRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<KYCRecord | null>(null);
  const [events, setEvents] = useState<KYCEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKYCRecords();
  }, []);

  const fetchKYCRecords = async () => {
    try {
      const response = await axios.get('/api/kyc/records/');
      setKycRecords(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch KYC records:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEvents = async (recordId: string) => {
    try {
      const response = await axios.get(`/api/kyc/records/${recordId}/events/`);
      setEvents(response.data);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const selectRecord = (record: KYCRecord) => {
    setSelectedRecord(record);
    fetchEvents(record.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'green';
      case 'rejected': return 'red';
      case 'in_progress': return 'blue';
      case 'pending': return 'orange';
      default: return 'gray';
    }
  };

  if (loading) {
    return <div>Loading KYC dashboard...</div>;
  }

  return (
    <div className="kyc-dashboard">
      <h2>KYC Management Dashboard</h2>
      
      <div className="dashboard-layout">
        <div className="records-list">
          <h3>KYC Records</h3>
          {kycRecords.map(record => (
            <div 
              key={record.id}
              className={`record-item ${selectedRecord?.id === record.id ? 'selected' : ''}`}
              onClick={() => selectRecord(record)}
            >
              <div className="record-header">
                <span className="user-name">{record.first_name} {record.last_name}</span>
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(record.status) }}
                >
                  {record.status}
                </span>
              </div>
              <div className="record-details">
                <small>{record.user_email}</small>
                <small>{new Date(record.created_at).toLocaleDateString()}</small>
              </div>
            </div>
          ))}
        </div>

        {selectedRecord && (
          <div className="record-details-panel">
            <h3>KYC Details</h3>
            
            <div className="details-grid">
              <div className="detail-item">
                <label>Name:</label>
                <span>{selectedRecord.first_name} {selectedRecord.last_name}</span>
              </div>
              
              <div className="detail-item">
                <label>Email:</label>
                <span>{selectedRecord.user_email}</span>
              </div>
              
              <div className="detail-item">
                <label>Status:</label>
                <span>{selectedRecord.status}</span>
              </div>
              
              <div className="detail-item">
                <label>Verification Level:</label>
                <span>{selectedRecord.verification_level}</span>
              </div>
              
              <div className="detail-item">
                <label>Created:</label>
                <span>{new Date(selectedRecord.created_at).toLocaleString()}</span>
              </div>
              
              {selectedRecord.verified_at && (
                <div className="detail-item">
                  <label>Verified:</label>
                  <span>{new Date(selectedRecord.verified_at).toLocaleString()}</span>
                </div>
              )}
            </div>

            <div className="events-section">
              <h4>Events History</h4>
              {events.map(event => (
                <div key={event.id} className="event-item">
                  <div className="event-type">{event.event_type}</div>
                  <div className="event-description">{event.description}</div>
                  <div className="event-timestamp">
                    {new Date(event.created_at).toLocaleString()}
                    {event.created_by_email && (
                      <span className="event-user"> by {event.created_by_email}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KYCDashboard;


// frontend/src/services/kycApi.ts

import axios from 'axios';

export interface KYCFormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  nationality: string;
  document_type: string;
  document_number: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
}

export interface KYCResponse {
  message: string;
  session_url: string;
  session_id: string;
  kyc_record: any;
}

export interface KYCStatus {
  kyc_status: string;
  is_verified: boolean;
  verification_level: string;
  created_at?: string;
  verified_at?: string;
  expires_at?: string;
}

class KYCApiService {
  private baseURL = '/api/kyc';

  async getSummary(): Promise<KYCStatus> {
    const response = await axios.get(`${this.baseURL}/summary/`);
    return response.data;
  }

  async startVerification(data: KYCFormData): Promise<KYCResponse> {
    const response = await axios.post(`${this.baseURL}/records/start_verification/`, data);
    return response.data;
  }

  async getStatus(recordId: string) {
    const response = await axios.get(`${this.baseURL}/records/${recordId}/status/`);
    return response.data;
  }

  async getEvents(recordId: string) {
    const response = await axios.get(`${this.baseURL}/records/${recordId}/events/`);
    return response.data;
  }

  async getRecords() {
    const response = await axios.get(`${this.baseURL}/records/`);
    return response.data;
  }
}

export const kycApi = new KYCApiService();