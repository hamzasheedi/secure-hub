// Button component
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick, 
  className = '',
  ...props 
}) => {
  const baseClasses = 'font-medium rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-gradient-to-r from-[#6C63FF] to-[#9B5DE5] hover:from-[#5C53EF] hover:to-[#8B4DD5] text-white focus:ring-[#6C63FF]',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-white focus:ring-gray-500',
    danger: 'bg-[#FF5252] hover:bg-[#FF4141] text-white focus:ring-[#FF5252]',
    success: 'bg-[#4CAF50] hover:bg-[#43A047] text-white focus:ring-[#4CAF50]',
    outline: 'border border-gray-600 text-gray-300 hover:bg-gray-700 focus:ring-gray-500'
  };
  
  const sizes = {
    sm: 'text-xs py-1.5 px-3',
    md: 'text-sm py-2 px-4',
    lg: 'text-base py-2.5 px-5'
  };
  
  const disabledClass = disabled ? 'opacity-50 cursor-not-allowed' : '';
  
  const classes = `${baseClasses} ${variants[variant]} ${sizes[size]} ${disabledClass} ${className}`;
  
  return (
    <button 
      className={classes} 
      onClick={onClick} 
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

// Card component
export const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-[#2C2C3E] border border-gray-700 rounded-xl ${className}`}>
      {children}
    </div>
  );
};

Card.Header = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-b border-gray-700 ${className}`}>
      {children}
    </div>
  );
};

Card.Body = ({ children, className = '' }) => {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  );
};

Card.Footer = ({ children, className = '' }) => {
  return (
    <div className={`px-6 py-4 border-t border-gray-700 ${className}`}>
      {children}
    </div>
  );
};

// Input component
export const Input = ({ 
  label, 
  id, 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  error, 
  required = false,
  className = ''
}) => {
  return (
    <div className="mb-4">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-300 mb-1">
          {label} {required && <span className="text-red-400">*</span>}
        </label>
      )}
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        className={`w-full px-3 py-2 bg-[#252536] border ${
          error ? 'border-red-500' : 'border-gray-600'
        } rounded-md text-white focus:outline-none focus:ring-2 focus:ring-[#6C63FF] focus:border-transparent ${className}`}
      />
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  );
};

// FileUpload component
export const FileUpload = ({ 
  onFilesSelected,
  allowedTypes = ['image/jpeg', 'image/png', 'application/pdf', 'application/zip', 'text/plain'],
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = true,
  label = "Select Files",
  description = "Supports: JPEG, PNG, PDF, ZIP, TXT (Max 10MB each)"
}) => {
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    
    // Validate files
    const validFiles = files.filter(file => {
      if (!allowedTypes.includes(file.type)) {
        alert(`File type not supported: ${file.type}. Only ${allowedTypes.join(', ')} files are allowed.`);
        return false;
      }
      
      if (file.size > maxSize) {
        alert(`File too large: ${file.name}. Maximum size is ${(maxSize / 1024 / 1024).toFixed(2)}MB.`);
        return false;
      }
      
      return true;
    });
    
    if (validFiles.length > 0) {
      onFilesSelected(validFiles);
    }
  };

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        {label}
      </label>
      <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed border-gray-600 rounded-md hover:border-[#6C63FF] transition-colors duration-200">
        <div className="space-y-1 text-center">
          <div className="flex text-sm text-gray-500">
            <label
              htmlFor="file-upload"
              className="relative cursor-pointer bg-[#252536] rounded-md font-medium text-[#6C63FF] hover:text-[#5C53EF] focus-without:outline-none"
            >
              <span>Upload a file</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                onChange={handleFileChange}
                multiple={multiple}
              />
            </label>
            <p className="pl-1">or drag and drop</p>
          </div>
          <p className="text-xs text-gray-400">{description}</p>
        </div>
      </div>
    </div>
  );
};