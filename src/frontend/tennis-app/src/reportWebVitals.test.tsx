import reportWebVitals from './reportWebVitals';

describe('reportWebVitals', () => {
  test('calls web vitals functions when valid handler is provided', () => {
    const mockHandler = jest.fn();
    
    // Mock web-vitals module
    jest.mock('web-vitals', () => ({
      getCLS: (handler: Function) => handler({ name: 'CLS', value: 0.1, delta: 0.1 }),
      getFID: (handler: Function) => handler({ name: 'FID', value: 100, delta: 100 }),
      getFCP: (handler: Function) => handler({ name: 'FCP', value: 200, delta: 200 }),
      getLCP: (handler: Function) => handler({ name: 'LCP', value: 300, delta: 300 }),
      getTTFB: (handler: Function) => handler({ name: 'TTFB', value: 400, delta: 400 }),
    }));

    reportWebVitals(mockHandler);

    // Wait for dynamic import
    setTimeout(() => {
      expect(mockHandler).toHaveBeenCalledTimes(5);
      expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({ name: 'CLS' }));
      expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({ name: 'FID' }));
      expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({ name: 'FCP' }));
      expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({ name: 'LCP' }));
      expect(mockHandler).toHaveBeenCalledWith(expect.objectContaining({ name: 'TTFB' }));
    });
  });

  test('does not call web vitals functions when no handler is provided', () => {
    const importSpy = jest.spyOn(Promise.prototype, 'then');
    
    reportWebVitals();
    
    expect(importSpy).not.toHaveBeenCalled();
    importSpy.mockRestore();
  });

  test('does not call web vitals functions when non-function handler is provided', () => {
    const importSpy = jest.spyOn(Promise.prototype, 'then');
    
    reportWebVitals('not a function' as any);
    
    expect(importSpy).not.toHaveBeenCalled();
    importSpy.mockRestore();
  });
});
