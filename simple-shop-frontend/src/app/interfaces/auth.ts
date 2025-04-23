export interface AuthResponse {
    access: string;
    refresh?: string;
    user?: User;
  }
  
  export interface User {
    id: number;
    username: string;
    email: string;
  }