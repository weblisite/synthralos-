import { CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';

interface ConnectionStatusProps {
  status: 'connected' | 'disconnected' | 'pending' | 'error';
  className?: string;
}

export function ConnectionStatus({ status, className = "" }: ConnectionStatusProps) {
  const statusConfig = {
    connected: {
      icon: <CheckCircle2 className="w-5 h-5 text-green-500" />,
      text: 'Connected',
      className: 'text-green-600'
    },
    disconnected: {
      icon: <XCircle className="w-5 h-5 text-gray-400" />,
      text: 'Not Connected',
      className: 'text-gray-500'
    },
    pending: {
      icon: <Clock className="w-5 h-5 text-yellow-500" />,
      text: 'Connecting...',
      className: 'text-yellow-600'
    },
    error: {
      icon: <AlertCircle className="w-5 h-5 text-red-500" />,
      text: 'Connection Error',
      className: 'text-red-600'
    }
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  return (
    <div className={`flex items-center gap-2 ${config.className} ${className}`}>
      {config.icon}
      <span className="text-sm font-medium">{config.text}</span>
    </div>
  );
}


