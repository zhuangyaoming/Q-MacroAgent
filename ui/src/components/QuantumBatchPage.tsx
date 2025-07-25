import React, { useState, useRef, useEffect } from 'react';
import QuantumBatchForm from './QuantumBatchForm';
import QuantumBatchStatus from './QuantumBatchStatus';
import QuantumBatchResults from './QuantumBatchResults';
import { glassStyle } from '../styles';

interface Company {
  name: string;
  industry: string;
  company_url: string;
  hq_location: string;
}

interface QuantumBatchFormData {
  companies: Company[];
  quantum_enabled: boolean;
  max_companies: number;
  quantum_layers: number;
  quantum_shots: number;
}

interface QuantumBatchPageProps {
  API_URL: string;
  WS_URL: string;
}

const QuantumBatchPage: React.FC<QuantumBatchPageProps> = ({ API_URL, WS_URL }) => {
  const [isResearching, setIsResearching] = useState(false);
  const [status, setStatus] = useState<string>('idle');
  const [message, setMessage] = useState<string>('');
  const [currentPhase, setCurrentPhase] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [companies, setCompanies] = useState<string[]>([]);
  
  const wsRef = useRef<WebSocket | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  const loaderColor = '#3b82f6';

  // WebSocket connection
  const connectWebSocket = (jobId: string) => {
    const wsUrl = `${WS_URL}/research/ws/${jobId}`;
    
    try {
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected for quantum batch analysis');
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);
          
          setStatus(data.status || 'processing');
          setMessage(data.message || '');
          
          // Extract phase information from message
          if (data.message) {
            if (data.message.includes('Collecting high-quality data')) {
              setCurrentPhase('data_collection');
              setProgress(20);
            } else if (data.message.includes('Quantum encoding')) {
              setCurrentPhase('quantum_encoding');
              setProgress(40);
            } else if (data.message.includes('parallel processing')) {
              setCurrentPhase('quantum_processing');
              setProgress(60);
            } else if (data.message.includes('Generating quantum-enhanced')) {
              setCurrentPhase('report_generation');
              setProgress(80);
            } else if (data.message.includes('completed')) {
              setCurrentPhase('knowledge_base');
              setProgress(100);
            }
          }
          
          if (data.status === 'completed') {
            setIsResearching(false);
            setResults(data.result);
            setProgress(100);
          } else if (data.status === 'failed' || data.status === 'error') {
            setIsResearching(false);
            setError(data.message || 'Analysis failed');
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };
      
      wsRef.current.onclose = () => {
        console.log('WebSocket connection closed');
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      setError('Failed to establish WebSocket connection');
    }
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSubmit = async (formData: QuantumBatchFormData) => {
    setIsResearching(true);
    setStatus('processing');
    setMessage('正在启动量子并行分析...');
    setError(null);
    setResults(null);
    setProgress(0);
    setCurrentPhase('');
    setCompanies(formData.companies.map(c => c.name));

    try {
      const response = await fetch(`${API_URL}/research/quantum-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Quantum batch research started:', data);
      
      setJobId(data.job_id);
      setMessage(data.message || '量子并行分析已启动');
      
      // Connect WebSocket for real-time updates
      if (data.job_id) {
        connectWebSocket(data.job_id);
      }
      
    } catch (error) {
      console.error('Error starting quantum batch research:', error);
      setError(error instanceof Error ? error.message : 'Failed to start analysis');
      setIsResearching(false);
      setStatus('error');
    }
  };

  const resetAnalysis = () => {
    setIsResearching(false);
    setStatus('idle');
    setMessage('');
    setCurrentPhase('');
    setProgress(0);
    setResults(null);
    setError(null);
    setCompanies([]);
    setJobId(null);
    
    if (wsRef.current) {
      wsRef.current.close();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 p-4">
      <div className="container mx-auto py-8">
        {/* Navigation */}
        <div className="mb-8">
          <button
            onClick={resetAnalysis}
            className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2"
          >
            ← 返回新分析
          </button>
        </div>

        {/* Content based on state */}
        {!isResearching && !results && !error && (
          <QuantumBatchForm
            onSubmit={handleSubmit}
            isResearching={isResearching}
            glassStyle={glassStyle}
            loaderColor={loaderColor}
          />
        )}

        {(isResearching || (status !== 'idle' && !results)) && (
          <QuantumBatchStatus
            status={status}
            message={message}
            companies={companies}
            currentPhase={currentPhase}
            progress={progress}
            glassStyle={glassStyle}
          />
        )}

        {results && (
          <div>
            <QuantumBatchResults
              results={results}
              glassStyle={glassStyle}
            />
            <div className="text-center mt-8">
              <button
                onClick={resetAnalysis}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105"
              >
                开始新的分析
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className={`${glassStyle.card} p-8 text-center`}>
            <div className="text-red-400 text-xl font-semibold mb-4">
              分析失败
            </div>
            <div className="text-gray-300 mb-6">
              {error}
            </div>
            <button
              onClick={resetAnalysis}
              className="px-6 py-3 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white font-semibold rounded-lg transition-all duration-300"
            >
              重新开始
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuantumBatchPage;
