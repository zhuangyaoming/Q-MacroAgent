import React from 'react';
import { 
  Atom, 
  Loader2, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Zap, 
  Activity,
  Database,
  Network
} from 'lucide-react';

interface QuantumBatchStatusProps {
  status: string;
  message: string;
  companies?: string[];
  currentPhase?: string;
  progress?: number;
  glassStyle: {
    card: string;
    input: string;
  };
}

const QuantumBatchStatus: React.FC<QuantumBatchStatusProps> = ({
  status,
  message,
  companies = [],
  currentPhase,
  progress = 0,
  glassStyle
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-8 h-8 text-green-400" />;
      case 'failed':
      case 'error':
        return <XCircle className="w-8 h-8 text-red-400" />;
      default:
        return <Clock className="w-8 h-8 text-yellow-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'text-blue-400';
      case 'completed':
        return 'text-green-400';
      case 'failed':
      case 'error':
        return 'text-red-400';
      default:
        return 'text-yellow-400';
    }
  };

  const getPhaseIcon = (phase: string) => {
    switch (phase) {
      case 'data_collection':
        return <Database className="w-5 h-5 text-blue-400" />;
      case 'quantum_encoding':
        return <Atom className="w-5 h-5 text-purple-400 animate-spin" style={{ animationDuration: '2s' }} />;
      case 'quantum_processing':
        return <Zap className="w-5 h-5 text-yellow-400" />;
      case 'report_generation':
        return <Activity className="w-5 h-5 text-green-400" />;
      case 'knowledge_base':
        return <Network className="w-5 h-5 text-cyan-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getPhaseLabel = (phase: string) => {
    switch (phase) {
      case 'data_collection':
        return 'Tavily数据收集';
      case 'quantum_encoding':
        return '量子编码';
      case 'quantum_processing':
        return '量子并行计算';
      case 'report_generation':
        return '融合分析报告';
      case 'knowledge_base':
        return '知识库保存';
      default:
        return '准备中';
    }
  };

  const phases = [
    'data_collection',
    'quantum_encoding', 
    'quantum_processing',
    'report_generation',
    'knowledge_base'
  ];

  const getCurrentPhaseIndex = () => {
    return phases.indexOf(currentPhase || '');
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className={`${glassStyle.card} p-8`}>
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            {getStatusIcon()}
            <h2 className="text-2xl font-bold text-white">
              量子并行分析状态
            </h2>
          </div>
          <p className={`text-lg ${getStatusColor()}`}>
            {message}
          </p>
        </div>

        {/* Companies List */}
        {companies.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Atom className="w-5 h-5 text-blue-400" />
              分析公司列表 ({companies.length})
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {companies.map((company, index) => (
                <div 
                  key={index}
                  className="p-3 bg-black/20 rounded-lg border border-white/10 text-center"
                >
                  <div className="text-white font-medium">{company}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {status === 'processing' && (
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-400">整体进度</span>
              <span className="text-sm text-blue-400">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Phase Progress */}
        {status === 'processing' && currentPhase && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-white mb-4">处理阶段</h3>
            <div className="space-y-3">
              {phases.map((phase, index) => {
                const isActive = phase === currentPhase;
                const isCompleted = index < getCurrentPhaseIndex();
                const isCurrent = index === getCurrentPhaseIndex();
                
                return (
                  <div 
                    key={phase}
                    className={`
                      flex items-center gap-3 p-3 rounded-lg border transition-all duration-300
                      ${isActive || isCurrent 
                        ? 'bg-blue-500/20 border-blue-500/40' 
                        : isCompleted 
                          ? 'bg-green-500/20 border-green-500/40'
                          : 'bg-black/20 border-white/10'
                      }
                    `}
                  >
                    <div className={`
                      flex items-center justify-center w-8 h-8 rounded-full
                      ${isCompleted 
                        ? 'bg-green-500/30' 
                        : isCurrent 
                          ? 'bg-blue-500/30' 
                          : 'bg-gray-500/30'
                      }
                    `}>
                      {isCompleted ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : isCurrent ? (
                        getPhaseIcon(phase)
                      ) : (
                        <Clock className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                    
                    <div className="flex-1">
                      <div className={`
                        font-medium
                        ${isCompleted 
                          ? 'text-green-400' 
                          : isCurrent 
                            ? 'text-blue-400' 
                            : 'text-gray-400'
                        }
                      `}>
                        {getPhaseLabel(phase)}
                      </div>
                      {isCurrent && (
                        <div className="text-sm text-gray-400 mt-1">
                          正在处理中...
                        </div>
                      )}
                    </div>
                    
                    {isCurrent && (
                      <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Status-specific content */}
        {status === 'completed' && (
          <div className="text-center p-6 bg-green-500/10 rounded-lg border border-green-500/20">
            <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
            <h3 className="text-xl font-semibold text-green-400 mb-2">
              量子并行分析完成！
            </h3>
            <p className="text-gray-300">
              所有公司的量子增强报告已生成并保存到知识库
            </p>
          </div>
        )}

        {(status === 'failed' || status === 'error') && (
          <div className="text-center p-6 bg-red-500/10 rounded-lg border border-red-500/20">
            <XCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
            <h3 className="text-xl font-semibold text-red-400 mb-2">
              分析失败
            </h3>
            <p className="text-gray-300">
              {message || '量子并行分析过程中出现错误，请重试'}
            </p>
          </div>
        )}

        {/* Quantum Animation */}
        {status === 'processing' && (
          <div className="text-center mt-8">
            <div className="flex items-center justify-center gap-2 text-blue-400">
              <Atom className="w-6 h-6 animate-spin" style={{ animationDuration: '3s' }} />
              <span className="text-lg font-medium">量子叠加态计算中</span>
              <Zap className="w-6 h-6 animate-pulse" />
            </div>
            <p className="text-gray-400 text-sm mt-2">
              利用量子纠缠发现公司间隐含关联...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuantumBatchStatus;
