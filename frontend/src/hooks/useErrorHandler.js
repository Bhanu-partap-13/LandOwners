import { useState, useEffect } from 'react';

// Hook for error handling in functional components
export const useErrorHandler = () => {
  const [error, setError] = useState(null);

  useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return setError;
};
