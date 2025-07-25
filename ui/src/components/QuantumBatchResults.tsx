import React, { useState } from 'react';
import { 
  Atom, 
  Building2, 
  TrendingUp, 
  Network, 
  Zap, 
  Download, 
  Eye, 
  ChevronDown, 
  ChevronUp,
  BarChart3,
  Activity
} from 'lucide-react';

interface QuantumMetadata {
  quantum_advantage_score: number;
  entanglement_strength: number;
  measurement_probability: number;
  quantum_features: number[];
  processing_timestamp: string;
  quantum_backend: string;
  shots_used: number;
  quantum_layers: number;
  total_qubits: number;
}

interface CompanyReport {
  company_name: string;
  tavily_report: string;
  quantum_enhanced_analysis: string;
  analysis_metadata: {
    quantum_metadata: QuantumMetadata;
    tavily_data: any;
  };
}

interface BatchSummary {
  batch_id: string;
  timestamp: string;
  analysis_type: string;
  total_companies: number;
  successful_count: number;
  companies_analyzed: string[];
  quantum_parameters: {
    total_qubits: number;
    quantum_layers: number;
    measurement_shots: number;
    max_companies: number;
  };
  quantum_statistics: {
    avg_quantum_advantage: number;
    avg_entanglement_strength: number;
  };
}

interface QuantumBatchResultsProps {
  results: {
    successful_reports: Record<string, CompanyReport>;
    batch_summary: BatchSummary;
    quantum_metadata: any;
  };
  glassStyle: {
    card: string;
    input: string;
  };
}

const QuantumBatchResults: React.FC<QuantumBatchResultsProps> = ({
  results,
  glassStyle
}) => {
  const [expandedCompany, setExpandedCompany] = useState<string | null>(null);
  const [showQuantumDetails, setShowQuantumDetails] = useState(false);

  const { successful_reports, batch_summary, quantum_metadata } = results;

  const getQuantumScoreColor = (score: number) => {
    if (score > 0.7) return 'text-green-400';
    if (score > 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getQuantumScoreLabel = (score: number) => {
    if (score > 0.7) return '高';
    if (score > 0.4) return '中';
    return '低';
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  const downloadReport = (companyName: string, report: CompanyReport) => {
    const content = JSON.stringify(report, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${companyName}_quantum_report.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Atom className="w-8 h-8 text-blue-400 animate-pulse" />
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            量子并行分析结果
          </h2>
          <Activity className="w-8 h-8 text-purple-400" />
        </div>
        <p className="text-gray-400">
          批次ID: {batch_summary?.batch_id} • 完成时间: {formatTimestamp(batch_summary?.timestamp)}
        </p>
      </div>

      {/* Batch Summary */}
      <div className={`${glassStyle.card} p-6`}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            批量分析摘要
          </h3>
          <button
            onClick={() => setShowQuantumDetails(!showQuantumDetails)}
            className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
          >
            量子参数详情
            {showQuantumDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-500/10 rounded-lg border border-blue-500/20">
            <div className="text-2xl font-bold text-blue-400">{batch_summary?.successful_count}</div>
            <div className="text-sm text-gray-400">成功分析</div>
          </div>
          <div className="text-center p-4 bg-green-500/10 rounded-lg border border-green-500/20">
            <div className="text-2xl font-bold text-green-400">
              {batch_summary?.quantum_statistics?.avg_quantum_advantage?.toFixed(3)}
            </div>
            <div className="text-sm text-gray-400">平均量子优势</div>
          </div>
          <div className="text-center p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <div className="text-2xl font-bold text-purple-400">
              {batch_summary?.quantum_statistics?.avg_entanglement_strength?.toFixed(3)}
            </div>
            <div className="text-sm text-gray-400">平均纠缠强度</div>
          </div>
          <div className="text-center p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
            <div className="text-2xl font-bold text-yellow-400">
              {batch_summary?.quantum_parameters?.total_qubits}
            </div>
            <div className="text-sm text-gray-400">量子比特数</div>
          </div>
        </div>

        {showQuantumDetails && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-black/20 rounded-lg border border-white/10">
            <div>
              <div className="text-sm text-gray-400">量子线路层数</div>
              <div className="text-lg font-semibold text-white">{batch_summary?.quantum_parameters?.quantum_layers}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">测量次数</div>
              <div className="text-lg font-semibold text-white">{batch_summary?.quantum_parameters?.measurement_shots}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400">分析类型</div>
              <div className="text-lg font-semibold text-white">{batch_summary?.analysis_type}</div>
            </div>
          </div>
        )}
      </div>

      {/* Company Results */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <Building2 className="w-5 h-5" />
          公司分析结果
        </h3>

        {Object.entries(successful_reports).map(([companyName, report]) => {
          const quantum = report.analysis_metadata.quantum_metadata;
          const isExpanded = expandedCompany === companyName;

          return (
            <div key={companyName} className={`${glassStyle.card} p-6`}>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Building2 className="w-6 h-6 text-blue-400" />
                  <h4 className="text-xl font-semibold text-white">{companyName}</h4>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => downloadReport(companyName, report)}
                    className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    title="下载报告"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setExpandedCompany(isExpanded ? null : companyName)}
                    className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Quantum Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="flex items-center gap-3 p-3 bg-black/20 rounded-lg">
                  <TrendingUp className={`w-5 h-5 ${getQuantumScoreColor(quantum.quantum_advantage_score)}`} />
                  <div>
                    <div className="text-sm text-gray-400">量子优势评分</div>
                    <div className={`font-semibold ${getQuantumScoreColor(quantum.quantum_advantage_score)}`}>
                      {quantum.quantum_advantage_score.toFixed(3)} ({getQuantumScoreLabel(quantum.quantum_advantage_score)})
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-black/20 rounded-lg">
                  <Network className={`w-5 h-5 ${getQuantumScoreColor(quantum.entanglement_strength)}`} />
                  <div>
                    <div className="text-sm text-gray-400">纠缠强度</div>
                    <div className={`font-semibold ${getQuantumScoreColor(quantum.entanglement_strength)}`}>
                      {quantum.entanglement_strength.toFixed(3)} ({getQuantumScoreLabel(quantum.entanglement_strength)})
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-black/20 rounded-lg">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <div>
                    <div className="text-sm text-gray-400">测量概率</div>
                    <div className="font-semibold text-yellow-400">
                      {quantum.measurement_probability.toFixed(3)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="space-y-4 border-t border-white/10 pt-4">
                  <div>
                    <h5 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                      <Atom className="w-4 h-4 text-blue-400" />
                      量子增强分析报告
                    </h5>
                    <div className="bg-black/20 rounded-lg p-4 max-h-96 overflow-y-auto">
                      <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                        {report.quantum_enhanced_analysis.substring(0, 2000)}
                        {report.quantum_enhanced_analysis.length > 2000 && '...'}
                      </pre>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">处理时间</div>
                      <div className="text-white">{formatTimestamp(quantum.processing_timestamp)}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">量子后端</div>
                      <div className="text-white">{quantum.quantum_backend}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">使用测量次数</div>
                      <div className="text-white">{quantum.shots_used}</div>
                    </div>
                    <div>
                      <div className="text-gray-400">量子比特数</div>
                      <div className="text-white">{quantum.total_qubits}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="text-center text-gray-400 text-sm">
        <p>🔬 基于wuyue量子框架的并行分析 • ⚡ 量子叠加态实现真正并行处理</p>
      </div>
    </div>
  );
};

export default QuantumBatchResults;
