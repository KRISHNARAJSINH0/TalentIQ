const GlassTable = ({ headers = [], children, className = '', style = {} }) => {
  return (
    <div className={`glass-table-container ${className}`} style={style}>
      <table className="glass-table">
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th key={index}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {children}
        </tbody>
      </table>
    </div>
  );
};

export default GlassTable;
