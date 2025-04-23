import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  // ngModel Bindings (2 total)
  credentials = { username: '', password: '' };
  errorMessage: string | null = null;
  isLoading = false;
  returnUrl: string = '/'; // Default return URL

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
    ) {
        // Get return url from route parameters or default to '/'
        this.route.queryParams.subscribe(params => {
            this.returnUrl = params['returnUrl'] || '/products'; // Redirect to products usually
        });
    }

  // Click Event 2 (API Call via AuthService triggered by submit)
  onLogin(): void {
    this.errorMessage = null;
    this.isLoading = true;
    this.authService.login(this.credentials).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate([this.returnUrl]); // Navigate to original or default URL
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.message || 'Login failed. Please check credentials.';
        console.error('Login error:', err);
      }
    });
  }
}