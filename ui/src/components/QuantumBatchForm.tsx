import React, { useState } from 'react';
import { Building2, Factory, Globe, Loader2, Plus, Trash2, Atom, Settings, Zap } from 'lucide-react';

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

interface QuantumBatchFormProps {
  onSubmit: (formData: QuantumBatchFormData) => Promise<void>;
  isResearching: boolean;
  glassStyle: {
    card: string;
    input: string;
  };
  loaderColor: string;
}

const QuantumBatchForm: React.FC<QuantumBatchFormProps> = ({
  onSubmit,
  isResearching,
  glassStyle,
  loaderColor
}) => {
  const [companies, setCompanies] = useState<Company[]>([
    { name: '', industry: '', company_url: '', hq_location: '' }
  ]);
  
  const [quantumSettings, setQuantumSettings] = useState({
    quantum_enabled: true,
    max_companies: 8,
    quantum_layers: 3,
    quantum_shots: 1000
  });
  
  const [showQuantumSettings, setShowQuantumSettings] = useState(false);

  const addCompany = () => {
    if (companies.length < quantumSettings.max_companies) {
      setCompanies([...companies, { name: '', industry: '', company_url: '', hq_location: '' }]);
    }
  };

  const removeCompany = (index: number) => {
    if (companies.length > 1) {
      setCompanies(companies.filter((_, i) => i !== index));
    }
  };

  const updateCompany = (index: number, field: keyof Company, value: string) => {
    const updated = companies.map((company, i) => 
      i === index ? { ...company, [field]: value } : company
    );
    setCompanies(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Filter out empty companies
    const validCompanies = companies.filter(company => company.name.trim());
    
    if (validCompanies.length === 0) {
      alert('请至少添加一家公司');
      return;
    }

    const formData: QuantumBatchFormData = {
      companies: validCompanies,
      ...quantumSettings
    };

    await onSubmit(formData);
  };

  const loadExampleCompanies = () => {
    setCompanies([
      { name: '特斯拉', industry: '汽车', company_url: 'https://www.tesla.com', hq_location: '美国' },
      { name: '小米', industry: '科技', company_url: 'https://www.mi.com', hq_location: '中国' },
      { name: 'Apple', industry: '科技', company_url: 'https://www.apple.com', hq_location: '美国' },
      { name: 'Vivo', industry: '科技', company_url: 'https://www.vivo.com', hq_location: '中国' }
    ]);
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Atom className="w-8 h-8 text-blue-400 animate-spin" style={{ animationDuration: '3s' }} />
          <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            量子并行分析
          </h2>
          <Zap className="w-8 h-8 text-purple-400" />
        </div>
        <p className="text-gray-400 text-lg">
          利用量子叠加态同时分析多家公司，发现隐含关联
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Companies Section */}
        <div className={`${glassStyle.card} p-6`}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5" />
              公司列表 ({companies.length}/{quantumSettings.max_companies})
            </h3>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={loadExampleCompanies}
                className="px-3 py-1 text-sm bg-blue-500/20 text-blue-300 rounded-lg hover:bg-blue-500/30 transition-colors"
              >
                加载示例
              </button>
              <button
                type="button"
                onClick={addCompany}
                disabled={companies.length >= quantumSettings.max_companies}
                className="flex items-center gap-1 px-3 py-1 text-sm bg-green-500/20 text-green-300 rounded-lg hover:bg-green-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4" />
                添加公司
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {companies.map((company, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-black/20 rounded-lg border border-white/10">
                <div className="relative">
                  <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="公司名称 *"
                    value={company.name}
                    onChange={(e) => updateCompany(index, 'name', e.target.value)}
                    className={`${glassStyle.input} pl-10`}
                    required
                  />
                </div>
                
                <div className="relative">
                  <Factory className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="行业"
                    value={company.industry}
                    onChange={(e) => updateCompany(index, 'industry', e.target.value)}
                    className={`${glassStyle.input} pl-10`}
                  />
                </div>
                
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="url"
                    placeholder="公司网址"
                    value={company.company_url}
                    onChange={(e) => updateCompany(index, 'company_url', e.target.value)}
                    className={`${glassStyle.input} pl-10`}
                  />
                </div>
                
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="总部位置"
                    value={company.hq_location}
                    onChange={(e) => updateCompany(index, 'hq_location', e.target.value)}
                    className={`${glassStyle.input} flex-1`}
                  />
                  {companies.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCompany(index)}
                      className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quantum Settings */}
        <div className={`${glassStyle.card} p-6`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
              <Settings className="w-5 h-5" />
              量子计算参数
            </h3>
            <button
              type="button"
              onClick={() => setShowQuantumSettings(!showQuantumSettings)}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              {showQuantumSettings ? '隐藏' : '显示'}
            </button>
          </div>

          <div className="flex items-center gap-4 mb-4">
            <label className="flex items-center gap-2 text-white">
              <input
                type="checkbox"
                checked={quantumSettings.quantum_enabled}
                onChange={(e) => setQuantumSettings(prev => ({ ...prev, quantum_enabled: e.target.checked }))}
                className="w-4 h-4 text-blue-500 bg-transparent border-gray-300 rounded focus:ring-blue-500"
              />
              启用量子增强分析
            </label>
            {quantumSettings.quantum_enabled && (
              <span className="text-green-400 text-sm flex items-center gap-1">
                <Atom className="w-4 h-4" />
                量子模式已激活
              </span>
            )}
          </div>

          {showQuantumSettings && quantumSettings.quantum_enabled && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  最大公司数量
                </label>
                <input
                  type="number"
                  min="2"
                  max="16"
                  value={quantumSettings.max_companies}
                  onChange={(e) => setQuantumSettings(prev => ({ ...prev, max_companies: parseInt(e.target.value) }))}
                  className={glassStyle.input}
                />
                <p className="text-xs text-gray-400 mt-1">影响量子比特需求</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  量子线路层数
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={quantumSettings.quantum_layers}
                  onChange={(e) => setQuantumSettings(prev => ({ ...prev, quantum_layers: parseInt(e.target.value) }))}
                  className={glassStyle.input}
                />
                <p className="text-xs text-gray-400 mt-1">影响分析复杂度</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  量子测量次数
                </label>
                <input
                  type="number"
                  min="100"
                  max="10000"
                  step="100"
                  value={quantumSettings.quantum_shots}
                  onChange={(e) => setQuantumSettings(prev => ({ ...prev, quantum_shots: parseInt(e.target.value) }))}
                  className={glassStyle.input}
                />
                <p className="text-xs text-gray-400 mt-1">影响结果精度</p>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="text-center">
          <button
            type="submit"
            disabled={isResearching || companies.filter(c => c.name.trim()).length === 0}
            className={`
              px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 transform
              ${isResearching 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 hover:scale-105 shadow-lg hover:shadow-xl'
              }
              text-white flex items-center gap-3 mx-auto
            `}
          >
            {isResearching ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" style={{ color: loaderColor }} />
                量子分析进行中...
              </>
            ) : (
              <>
                <Atom className="w-5 h-5" />
                开始量子并行分析
                <Zap className="w-5 h-5" />
              </>
            )}
          </button>
          
          {!isResearching && (
            <p className="text-gray-400 text-sm mt-3">
              将同时分析 {companies.filter(c => c.name.trim()).length} 家公司
              {quantumSettings.quantum_enabled && (
                <span className="text-blue-400"> • 量子增强模式</span>
              )}
            </p>
          )}
        </div>
      </form>
    </div>
  );
};

export default QuantumBatchForm;
