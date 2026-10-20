



export function AuthCard({ title, subtitle, children }) {
  return (
    <div className="row justify-content-center">
      <div className="col-sm-10 col-md-7 col-lg-5">
        <div className="card border-0 shadow-sm">
          <div className="card-body p-4">
            <h1 className="h3 fw-bold">{title}</h1>
            <p className="text-secondary">{subtitle}</p>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}


export function Input({ label, name, id = name, ...props }) {
  return (
    <div className="mb-3">
      <label htmlFor={id} className="form-label fw-semibold">{label}</label>
      <input id={id} name={name} className="form-control" {...props} />
    </div>
  );
}


export function Alert({ type, text }) {
  return <div className={`alert alert-${type}`}>{text}</div>;
}


export function Loading() {
  return (
    <div className="d-flex justify-content-center align-items-center py-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Cargando...</span>
      </div>
    </div>
  );
}
