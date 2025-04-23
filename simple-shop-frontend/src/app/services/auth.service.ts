import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Router } from '@angular/router';
import { AuthResponse, User } from '../interfaces/auth';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private tokenKey = 'authToken';
  private userKey = 'authUser';

  private _isAuthenticated = new BehaviorSubject<boolean>(this.hasToken());
  isAuthenticated$ = this._isAuthenticated.asObservable();

  private _currentUser = new BehaviorSubject<User | null>(this.getUserFromStorage());
  currentUser$ = this._currentUser.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  login(credentials: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login/`, credentials).pipe(
      tap(response => this.handleAuthSuccess(response))
    );
  }

  register(userData: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/register/`, userData).pipe(
      tap(response => this.handleAuthSuccess(response))
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    this._isAuthenticated.next(false);
    this._currentUser.next(null);
    this.router.navigate(['/login']); // Navigate after clearing state
  }

  getToken(): string | null {
    return typeof localStorage !== 'undefined' ? localStorage.getItem(this.tokenKey) : null;
  }

  private getUserFromStorage(): User | null {
     if (typeof localStorage !== 'undefined') {
         const userStr = localStorage.getItem(this.userKey);
         return userStr ? JSON.parse(userStr) : null;
     }
     return null;
  }

  private hasToken(): boolean {
    return !!this.getToken();
  }

  private handleAuthSuccess(response: AuthResponse): void {
    if (response.access) {
      localStorage.setItem(this.tokenKey, response.access);
      if (response.user) {
        localStorage.setItem(this.userKey, JSON.stringify(response.user));
        this._currentUser.next(response.user);
      } else {
         // Handle case where user might not be returned (e.g., clear previous user)
         localStorage.removeItem(this.userKey);
         this._currentUser.next(null);
      }
      this._isAuthenticated.next(true);
    } else {
      console.error('Auth response missing access token.');
      this.logout();
    }
  }
}