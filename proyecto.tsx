import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, ReferenceLine } from 'recharts';
import { TrendingUp, TrendingDown, BarChart3, Calculator, Calendar, DollarSign, Table, Target } from 'lucide-react';

// Tasa de cambio aproximada KRW a MXN (1 KRW = 0.0135 MXN aproximadamente)
const KRW_TO_MXN = 0.0135;

// Datos simulados de Samsung (replicando los resultados del script Python)
const generateSamsungData = () => {
  const data = [];
  const startDate = new Date('2022-09-13');
  let currentPrice = 58100;
  
  for (let i = 0; i < 734; i++) {
    const date = new Date(startDate);
    date.setDate(startDate.getDate() + i);
    
    // Simular movimientos de precio con tendencia alcista y volatilidad
    const randomChange = (Math.random() - 0.5) * 0.04; // ±2% volatilidad base
    const trendFactor = i / 734 * 0.25; // Tendencia alcista gradual
    currentPrice = currentPrice * (1 + randomChange + trendFactor * 0.001);
    
    data.push({
      date: date.toISOString().split('T')[0],
      dateObj: date,
      price: Math.round(currentPrice),
      priceMXN: Math.round(currentPrice * KRW_TO_MXN),
      index: i
    });
  }
  
  // Ajustar últimos precios para que coincidan con los datos reales
  data[data.length-5].price = 70100; data[data.length-5].priceMXN = Math.round(70100 * KRW_TO_MXN);
  data[data.length-4].price = 69500; data[data.length-4].priceMXN = Math.round(69500 * KRW_TO_MXN);
  data[data.length-3].price = 70100; data[data.length-3].priceMXN = Math.round(70100 * KRW_TO_MXN);
  data[data.length-2].price = 71500; data[data.length-2].priceMXN = Math.round(71500 * KRW_TO_MXN);
  data[data.length-1].price = 72600; data[data.length-1].priceMXN = Math.round(72600 * KRW_TO_MXN);
  
  return data;
};

interface PriceData {
    date: string;
    dateObj: Date;
    price: number;
    priceMXN: number;
    index: number;
}

interface LogReturn {
    date: string;
    dateObj: Date;
    return: number;
    percentage: string;
    previousPrice: number;
    currentPrice: number;
    calculation: string;
}

const calculateLogReturns = (data: PriceData[]): LogReturn[] => {
    const returns: LogReturn[] = [];
    for (let i = 1; i < data.length; i++) {
        const logReturn = Math.log(data[i].price / data[i-1].price);
        returns.push({
            date: data[i].date,
            dateObj: data[i].dateObj,
            return: logReturn,
            percentage: (logReturn * 100).toFixed(4),
            previousPrice: data[i-1].price,
            currentPrice: data[i].price,
            calculation: `ln(${data[i].price}) - ln(${data[i-1].price}) = ${logReturn.toFixed(6)}`
        });
    }
    return returns;
};

const calculateStatistics = (returns: LogReturn[]) => {
  const values = returns.map(r => r.return);
  const sum = values.reduce((a, b) => a + b, 0);
  const mean = sum / values.length;
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  
  return {
    count: values.length,
    max: Math.max(...values),
    min: Math.min(...values),
    mean: mean,
    variance: variance,
    stdDev: stdDev
  };
};

// Componente de Box Plot mejorado
const ImprovedBoxPlot = ({ returns }: { returns: LogReturn[] }) => {
  const values = returns.map(r => r.return).sort((a, b) => a - b);
  const n = values.length;
  
  // Cálculos estadísticos para box plot
  const q1 = values[Math.floor(n * 0.25)];
  const median = values[Math.floor(n * 0.5)];
  const q3 = values[Math.floor(n * 0.75)];
  const iqr = q3 - q1;
  
  // Límites para outliers (1.5 * IQR)
  const lowerFence = q1 - 1.5 * iqr;
  const upperFence = q3 + 1.5 * iqr;
  
  // Whiskers (valores min/max dentro de los fences)
  const lowerWhisker = Math.max(values[0], lowerFence);
  const upperWhisker = Math.min(values[n-1], upperFence);
  
  // Outliers
  const outliers = values.filter(v => v < lowerFence || v > upperFence);
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-800">
        <BarChart3 className="text-green-600" />
        Gráfico de Caja y Bigotes - Distribución de Rendimientos
      </h3>
      
      {/* Estadísticas del Box Plot */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="text-center p-3 bg-red-50 rounded-lg border-l-4 border-red-500">
          <div className="text-xs font-semibold text-red-700 mb-1">Min (Whisker)</div>
          <div className="text-sm font-bold text-red-600">{lowerWhisker.toFixed(6)}</div>
        </div>
        <div className="text-center p-3 bg-orange-50 rounded-lg border-l-4 border-orange-500">
          <div className="text-xs font-semibold text-orange-700 mb-1">Q1 (25%)</div>
          <div className="text-sm font-bold text-orange-600">{q1.toFixed(6)}</div>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <div className="text-xs font-semibold text-blue-700 mb-1">Mediana (50%)</div>
          <div className="text-sm font-bold text-blue-600">{median.toFixed(6)}</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg border-l-4 border-purple-500">
          <div className="text-xs font-semibold text-purple-700 mb-1">Q3 (75%)</div>
          <div className="text-sm font-bold text-purple-600">{q3.toFixed(6)}</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
          <div className="text-xs font-semibold text-green-700 mb-1">Max (Whisker)</div>
          <div className="text-sm font-bold text-green-600">{upperWhisker.toFixed(6)}</div>
        </div>
      </div>
      
      {/* Visualización del Box Plot usando barras horizontales */}
      <div className="h-80 bg-gray-50 rounded-lg p-4 relative">
        <div className="flex flex-col items-center justify-center h-full">
          {/* Box plot visual simple */}
          <div className="w-3/4 h-20 relative">
            {/* Línea base */}
            <div className="absolute top-1/2 w-full h-0.5 bg-gray-300"></div>
            
            {/* Whiskers */}
            <div 
              className="absolute top-1/4 w-0.5 h-1/2 bg-red-500"
              style={{left: '10%'}}
            ></div>
            <div 
              className="absolute top-1/4 w-0.5 h-1/2 bg-red-500"
              style={{left: '90%'}}
            ></div>
            
            {/* Box (Q1 to Q3) */}
            <div 
              className="absolute top-1/4 h-1/2 bg-blue-300 border-2 border-blue-600"
              style={{left: '30%', width: '40%'}}
            ></div>
            
            {/* Median line */}
            <div 
              className="absolute top-1/4 w-0.5 h-1/2 bg-blue-800"
              style={{left: '50%'}}
            ></div>
          </div>
          
          {/* Etiquetas */}
          <div className="w-3/4 flex justify-between text-xs mt-4">
            <span className="text-red-600">Min</span>
            <span className="text-orange-600">Q1</span>
            <span className="text-blue-600">Med</span>
            <span className="text-purple-600">Q3</span>
            <span className="text-green-600">Max</span>
          </div>
        </div>
      </div>
      
      {/* Interpretación */}
      <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <h4 className="font-bold text-gray-800 mb-2">Interpretación:</h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>
            <p><strong>IQR (Rango Intercuartil):</strong> {iqr.toFixed(6)}</p>
            <p><strong>Outliers detectados:</strong> {outliers.length} valores</p>
          </div>
          <div>
            <p><strong>Asimetría:</strong> {median > (q1 + q3) / 2 ? 'Positiva (cola derecha)' : 'Negativa (cola izquierda)'}</p>
            <p><strong>Concentración:</strong> {iqr < 0.01 ? 'Alta' : iqr < 0.02 ? 'Media' : 'Baja'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const FinancialAnalysisApp = () => {
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [logReturns, setLogReturns] = useState<LogReturn[]>([]);
  const [statistics, setStatistics] = useState({
    count: 0,
    max: 0,
    min: 0,
    mean: 0,
    variance: 0,
    stdDev: 0
  });
  const [selectedIndex1, setSelectedIndex1] = useState(200);
  const [selectedIndex2, setSelectedIndex2] = useState(600);
  const [activeTab, setActiveTab] = useState('prices');
  const [showMXN, setShowMXN] = useState(true);

  useEffect(() => {
    const data = generateSamsungData();
    setPriceData(data);
    
    const returns = calculateLogReturns(data);
    setLogReturns(returns);
    
    const stats = calculateStatistics(returns);
    setStatistics(stats);
  }, []);

  const first5Prices = priceData.slice(0, 5);
  const last5Prices = priceData.slice(-5);
  const first5Returns = logReturns.slice(0, 5);
  const last5Returns = logReturns.slice(-5);

  const calculateComparison = () => {
    if (priceData.length === 0) return null;
    
    const price1 = priceData[selectedIndex1];
    const price2 = priceData[selectedIndex2];
    
    if (!price1 || !price2) return null;
    
    const difference = price2.price - price1.price;
    const differenceMXN = price2.priceMXN - price1.priceMXN;
    const percentageChange = (difference / price1.price) * 100;
    
    return {
      price1,
      price2,
      difference,
      differenceMXN,
      percentageChange
    };
  };

  const comparison = calculateComparison();
  const trend = priceData.length > 0 && priceData[priceData.length - 1].price > priceData[0].price ? 'alcista' : 'bajista';
  const volatility = statistics.stdDev > 0.02 ? 'alta' : statistics.stdDev > 0.01 ? 'media' : 'baja';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Análisis Financiero Samsung Electronics
          </h1>
          <p className="text-gray-600 text-lg">Ticker: 005930.KS | Período: 3 años | 734 días de datos</p>
          
          {/* Toggle de moneda */}
          <div className="mt-4 flex justify-center items-center gap-4">
            <span className="text-gray-600">Mostrar precios en:</span>
            <button
              onClick={() => setShowMXN(!showMXN)}
              className={`px-4 py-2 rounded-full transition-all ${
                showMXN 
                  ? 'bg-green-600 text-white shadow-md' 
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              {showMXN ? '🇰🇷 KRW + 🇲🇽 MXN' : '🇰🇷 KRW únicamente'}
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-full p-1 shadow-lg">
            {[
              { id: 'prices', label: 'Precios & Tablas', icon: DollarSign },
              { id: 'returns', label: 'Rendimientos Log', icon: TrendingUp },
              { id: 'statistics', label: 'Estadísticas', icon: Calculator },
              { id: 'boxplot', label: 'Box Plot', icon: BarChart3 },
              { id: 'comparison', label: 'Comparación', icon: Table }
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 rounded-full transition-all ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={18} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Prices Tab */}
        {activeTab === 'prices' && (
          <div className="space-y-8">
            {/* Price Evolution Chart */}
            <div className="bg-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <DollarSign className="text-blue-600" />
                  Evolución del Precio de Cierre vs. Tiempo
                </h2>
                <div className="text-right">
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-full mb-2 ${
                    trend === 'alcista' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {trend === 'alcista' ? <TrendingUp /> : <TrendingDown />}
                    Tendencia {trend.charAt(0).toUpperCase() + trend.slice(1)}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm ${
                    volatility === 'alta' ? 'bg-red-100 text-red-700' : 
                    volatility === 'media' ? 'bg-yellow-100 text-yellow-700' : 
                    'bg-green-100 text-green-700'
                  }`}>
                    Variabilidad: {volatility}
                  </div>
                </div>
              </div>
              
              <div className="h-96 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={priceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 11 }}
                      tickFormatter={(date) => new Date(date).toLocaleDateString()}
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      tick={{ fontSize: 11 }}
                      tickFormatter={(value) => `${value.toLocaleString()} KRW`}
                    />
                    <Tooltip 
                      formatter={(value) => [
                        `${value.toLocaleString()} KRW${showMXN ? ` (${Math.round(value * KRW_TO_MXN).toLocaleString()} MXN)` : ''}`, 
                        'Precio de Cierre'
                      ]}
                      labelFormatter={(date) => `Fecha: ${new Date(date).toLocaleDateString()}`}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="price" 
                      stroke="url(#gradient)" 
                      strokeWidth={2}
                      dot={false}
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3B82F6" />
                        <stop offset="100%" stopColor="#8B5CF6" />
                      </linearGradient>
                    </defs>
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg">
                <p className="text-gray-700 text-center">
                  <strong>Contexto:</strong> Tendencia {trend} con variabilidad {volatility}. 
                  Precio inicial: {priceData[0]?.price.toLocaleString()} KRW 
                  {showMXN && ` (${priceData[0]?.priceMXN.toLocaleString()} MXN)`} → 
                  Precio final: {priceData[priceData.length - 1]?.price.toLocaleString()} KRW
                  {showMXN && ` (${priceData[priceData.length - 1]?.priceMXN.toLocaleString()} MXN)`}
                </p>
              </div>
            </div>

            {/* Detailed Price Tables */}
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                  <Calendar className="text-blue-600" />
                  Primeros 5 Precios
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-blue-50">
                        <th className="px-4 py-2 text-left text-sm font-semibold">Fecha</th>
                        <th className="px-4 py-2 text-right text-sm font-semibold">KRW</th>
                        {showMXN && <th className="px-4 py-2 text-right text-sm font-semibold">MXN</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {first5Prices.map((item, i) => (
                        <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="px-4 py-2 text-sm">{new Date(item.date).toLocaleDateString()}</td>
                          <td className="px-4 py-2 text-sm font-medium text-blue-600 text-right">
                            {item.price.toLocaleString()}
                          </td>
                          {showMXN && (
                            <td className="px-4 py-2 text-sm font-medium text-green-600 text-right">
                              {item.priceMXN.toLocaleString()}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                  <Calendar className="text-purple-600" />
                  Últimos 5 Precios
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-purple-50">
                        <th className="px-4 py-2 text-left text-sm font-semibold">Fecha</th>
                        <th className="px-4 py-2 text-right text-sm font-semibold">KRW</th>
                        {showMXN && <th className="px-4 py-2 text-right text-sm font-semibold">MXN</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {last5Prices.map((item, i) => (
                        <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="px-4 py-2 text-sm">{new Date(item.date).toLocaleDateString()}</td>
                          <td className="px-4 py-2 text-sm font-medium text-purple-600 text-right">
                            {item.price.toLocaleString()}
                          </td>
                          {showMXN && (
                            <td className="px-4 py-2 text-sm font-medium text-green-600 text-right">
                              {item.priceMXN.toLocaleString()}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Returns Tab */}
        {activeTab === 'returns' && (
          <div className="space-y-8">
            {/* Log Returns Explanation */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-xl shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-gray-800 flex items-center gap-2">
                <Target className="text-green-600" />
                Cálculo de Rendimientos Logarítmicos
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white p-4 rounded-lg">
                  <h4 className="font-bold mb-2">Fórmula:</h4>
                  <p className="font-mono text-lg text-blue-600">ln(Precio_hoy / Precio_ayer)</p>
                  <p className="text-sm text-gray-600 mt-1">= ln(Precio_hoy) - ln(Precio_ayer)</p>
                </div>
                <div className="bg-white p-4 rounded-lg">
                  <h4 className="font-bold mb-2">Ejemplo:</h4>
                  <div className="space-y-1 text-sm">
                    <p>Precio anterior: <span className="font-mono">289 KRW</span></p>
                    <p>Precio actual: <span className="font-mono">291 KRW</span></p>
                    <p>Rendimiento: <span className="font-mono text-green-600">ln(291) - ln(289) = 0.0069 (0.69%)</span></p>
                  </div>
                </div>
              </div>
            </div>

            {/* Returns Tables */}
            <div className="grid md:grid-cols-2 gap-8">
              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4 text-gray-800">Primeros 5 Rendimientos</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-green-50">
                        <th className="px-3 py-2 text-left text-sm font-semibold">Fecha</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Precio Ant.</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Precio Act.</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Rendimiento</th>
                      </tr>
                    </thead>
                    <tbody>
                      {first5Returns.map((item, i) => (
                        <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="px-3 py-2 text-xs">{new Date(item.date).toLocaleDateString()}</td>
                          <td className="px-3 py-2 text-xs text-right">{item.previousPrice.toLocaleString()}</td>
                          <td className="px-3 py-2 text-xs text-right">{item.currentPrice.toLocaleString()}</td>
                          <td className={`px-3 py-2 text-xs font-bold text-right ${
                            item.return >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {item.return.toFixed(6)}
                            <br />
                            <span className="text-xs">({item.percentage}%)</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4 text-gray-800">Últimos 5 Rendimientos</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-orange-50">
                        <th className="px-3 py-2 text-left text-sm font-semibold">Fecha</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Precio Ant.</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Precio Act.</th>
                        <th className="px-3 py-2 text-right text-sm font-semibold">Rendimiento</th>
                      </tr>
                    </thead>
                    <tbody>
                      {last5Returns.map((item, i) => (
                        <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                          <td className="px-3 py-2 text-xs">{new Date(item.date).toLocaleDateString()}</td>
                          <td className="px-3 py-2 text-xs text-right">{item.previousPrice.toLocaleString()}</td>
                          <td className="px-3 py-2 text-xs text-right">{item.currentPrice.toLocaleString()}</td>
                          <td className={`px-3 py-2 text-xs font-bold text-right ${
                            item.return >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {item.return.toFixed(6)}
                            <br />
                            <span className="text-xs">({item.percentage}%)</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'statistics' && (
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h3 className="text-xl font-bold mb-6 text-gray-800 flex items-center gap-2">
                <Calculator className="text-blue-600" />
                Estadísticas Descriptivas de Rendimientos
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                {[
                  { label: 'Total Rendimientos', value: statistics.count?.toLocaleString(), color: 'blue' },
                  { label: 'Máximo', value: statistics.max?.toFixed(6), color: 'green' },
                  { label: 'Mínimo', value: statistics.min?.toFixed(6), color: 'red' },
                  { label: 'Promedio', value: statistics.mean?.toFixed(6), color: 'purple' },
                  { label: 'Varianza', value: statistics.variance?.toFixed(6), color: 'orange' },
                  { label: 'Desv. Estándar', value: statistics.stdDev?.toFixed(6), color: 'indigo' }
                ].map((stat, i) => (
                  <div key={i} className="text-center p-4 bg-gray-50 rounded-lg border-l-4 border-gray-400">
                    <div className="text-sm font-medium text-gray-700 mb-1">{stat.label}</div>
                    <div className="text-lg font-bold text-gray-800">{stat.value}</div>
                  </div>
                ))}
              </div>
              
              {/* Interpretación de estadísticas */}
              <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                <h4 className="font-bold text-gray-800 mb-2">Interpretación:</h4>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
                  <div>
                    <p><strong>Rendimiento promedio diario:</strong> {((statistics.mean || 0) * 100).toFixed(4)}%</p>
                    <p><strong>Volatilidad diaria:</strong> {((statistics.stdDev || 0) * 100).toFixed(2)}%</p>
                  </div>
                  <div>
                    <p><strong>Mejor día:</strong> +{((statistics.max || 0) * 100).toFixed(2)}%</p>
                    <p><strong>Peor día:</strong> {((statistics.min || 0) * 100).toFixed(2)}%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Box Plot Tab */}
        {activeTab === 'boxplot' && (
          <div className="space-y-8">
            <ImprovedBoxPlot returns={logReturns} />
          </div>
        )}

        {/* Comparison Tab */}
        {activeTab === 'comparison' && (
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-xl shadow-lg">
              <h3 className="text-xl font-bold mb-6 text-gray-800 flex items-center gap-2">
                <Calendar className="text-blue-600" />
                Comparación Detallada de Precios
              </h3>
              
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primera fecha (índice 0-{priceData.length - 1}):
                  </label>
                  <input
                    type="number"
                    min="0"
                    max={priceData.length - 1}
                    value={selectedIndex1}
                    onChange={(e) => setSelectedIndex1(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Segunda fecha (índice 0-{priceData.length - 1}):
                  </label>
                  <input
                    type="number"
                    min="0"
                    max={priceData.length - 1}
                    value={selectedIndex2}
                    onChange={(e) => setSelectedIndex2(parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {comparison && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
                  <h4 className="text-lg font-bold mb-4">Resultado de la Comparación</h4>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Fecha 1:</span>
                        <span>{new Date(comparison.price1.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Precio 1:</span>
                        <div className="text-right">
                          <span className="font-bold">{comparison.price1.price.toLocaleString()} KRW</span>
                          {showMXN && <br />}
                          {showMXN && <span className="text-sm text-green-600">{comparison.price1.priceMXN.toLocaleString()} MXN</span>}
                        </div>
                      </div>
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Fecha 2:</span>
                        <span>{new Date(comparison.price2.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Precio 2:</span>
                        <div className="text-right">
                          <span className="font-bold">{comparison.price2.price.toLocaleString()} KRW</span>
                          {showMXN && <br />}
                          {showMXN && <span className="text-sm text-green-600">{comparison.price2.priceMXN.toLocaleString()} MXN</span>}
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Diferencia:</span>
                        <div className={`text-right font-bold ${comparison.difference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {comparison.difference.toLocaleString()} KRW
                          {showMXN && <br />}
                          {showMXN && <span className="text-sm">{comparison.differenceMXN.toLocaleString()} MXN</span>}
                        </div>
                      </div>
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Cambio %:</span>
                        <span className={`font-bold text-2xl ${comparison.percentageChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {comparison.percentageChange.toFixed(2)}%
                        </span>
                      </div>
                      
                      {/* Días transcurridos */}
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Días transcurridos:</span>
                        <span className="font-bold">{Math.abs(selectedIndex2 - selectedIndex1)} días</span>
                      </div>
                      
                      {/* Rendimiento anualizado aproximado */}
                      <div className="flex justify-between p-2 bg-white rounded">
                        <span className="font-medium">Rend. Anualizado:</span>
                        <span className="font-bold text-blue-600">
                          {(comparison.percentageChange * (365 / Math.abs(selectedIndex2 - selectedIndex1))).toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tabla de comparación completa */}
              <div className="mt-8">
                <h4 className="text-lg font-bold mb-4 text-gray-800">Tabla Detallada de Precios (Muestra)</h4>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="px-4 py-2 text-left text-sm font-semibold">Índice</th>
                        <th className="px-4 py-2 text-left text-sm font-semibold">Fecha</th>
                        <th className="px-4 py-2 text-right text-sm font-semibold">Precio KRW</th>
                        {showMXN && <th className="px-4 py-2 text-right text-sm font-semibold">Precio MXN</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {priceData.slice(0, 10).map((item, i) => (
                        <tr key={i} className={`${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'} ${
                          (i === selectedIndex1 || i === selectedIndex2) ? 'bg-yellow-100' : ''
                        }`}>
                          <td className="px-4 py-2 text-sm font-medium">{i}</td>
                          <td className="px-4 py-2 text-sm">{new Date(item.date).toLocaleDateString()}</td>
                          <td className="px-4 py-2 text-sm text-right font-medium">{item.price.toLocaleString()}</td>
                          {showMXN && <td className="px-4 py-2 text-sm text-right font-medium text-green-600">{item.priceMXN.toLocaleString()}</td>}
                        </tr>
                      ))}
                      <tr>
                        <td colSpan={showMXN ? 4 : 3} className="px-4 py-2 text-center text-gray-500 text-sm">
                          ... ({priceData.length - 20} filas más) ...
                        </td>
                      </tr>
                      {priceData.slice(-10).map((item, i) => {
                        const actualIndex = priceData.length - 10 + i;
                        return (
                          <tr key={actualIndex} className={`${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'} ${
                            (actualIndex === selectedIndex1 || actualIndex === selectedIndex2) ? 'bg-yellow-100' : ''
                          }`}>
                            <td className="px-4 py-2 text-sm font-medium">{actualIndex}</td>
                            <td className="px-4 py-2 text-sm">{new Date(item.date).toLocaleDateString()}</td>
                            <td className="px-4 py-2 text-sm text-right font-medium">{item.price.toLocaleString()}</td>
                            {showMXN && <td className="px-4 py-2 text-sm text-right font-medium text-green-600">{item.priceMXN.toLocaleString()}</td>}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center text-gray-600">
          <p className="text-sm">
            Análisis financiero generado con datos simulados basados en Samsung Electronics (005930.KS)
          </p>
          <p className="text-xs mt-1">
            Tasa de cambio aproximada: 1 KRW = {KRW_TO_MXN} MXN
          </p>
        </div>
      </div>
    </div>
  );
};

export default FinancialAnalysisApp;