import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: false,
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  // ngModel Bindings (6 total > 4)
  userData = { username: '', email: '', password: '', password_confirm: '' };
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isLoading = false;

  constructor(private authService: AuthService, private router: Router) {}

  // Click Event 3 (API Call via AuthService triggered by submit)
  onRegister(): void {
    if (this.userData.password !== this.userData.password_confirm) {
        this.errorMessage = "Passwords do not match.";
        return;
    }
    this.errorMessage = null;
    this.successMessage = null;
    this.isLoading = true;

    this.authService.register(this.userData).subscribe({
        next: (response) => {
            this.isLoading = false;
            this.successMessage = 'Registration successful! Redirecting...';
            console.log('Registration successful', response);
            // Navigate to login or directly to products after a delay
            setTimeout(() => this.router.navigate(['/products']), 1500);
        },
        error: (err) => {
            this.isLoading = false;
            this.errorMessage = err.message || 'Registration failed. Please try again.';
            console.error('Registration error:', err);
        }
    });
  }
}