#!/usr/bin/env python3
"""
Generate randomized Active Directory content for ludus_bulk_ad_content role.
Uses Faker if available, falls back to simple random generation otherwise.

Usage: python generate_random_ad.py --config '{"user_count": 50, ...}' --domain "corp.local"
Output: JSON to stdout
"""

import argparse
import json
import random
import string
import sys
from typing import Any

# Try to import Faker, set flag if not available
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class SimpleRandomGenerator:
    """Fallback generator when Faker is not available."""
    
    FIRST_NAMES = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Charles", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth",
        "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty",
        "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]
    
    CITIES = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
        "Fort Worth", "Columbus", "Charlotte", "Seattle", "Denver", "Boston"
    ]
    
    def first_name(self) -> str:
        return random.choice(self.FIRST_NAMES)
    
    def last_name(self) -> str:
        return random.choice(self.LAST_NAMES)
    
    def city(self) -> str:
        return random.choice(self.CITIES)


class ADContentGenerator:
    """Generate randomized AD content."""
    
    DEFAULT_DEPARTMENTS = ["HR", "IT", "Sales", "Finance", "Marketing", "Engineering", "Operations", "Legal"]
    
    WEAK_PASSWORDS = [
        "Password1", "Welcome1", "Company123", "Summer2024", "Winter2024",
        "Password123", "Qwerty123", "Letmein1", "Admin123", "User1234",
        "Changeme1", "Temp1234", "Test1234", "Guest123", "P@ssw0rd"
    ]
    
    def __init__(self, domain: str, config: dict[str, Any]):
        self.domain = domain
        self.config = config
        self.dc_path = self._domain_to_dc_path(domain)
        
        # Initialize generator
        if FAKER_AVAILABLE:
            self.fake = Faker()
            self.use_faker = True
        else:
            self.fake = SimpleRandomGenerator()
            self.use_faker = False
            print(f"[INFO] Faker not available, using simple random generation", file=sys.stderr)
        
        # Parse config
        self.user_count = config.get("user_count", 30)
        self.ou_count = config.get("ou_count", 5)
        self.group_count = config.get("group_count", 8)
        self.password_style = config.get("password_style", "weak")
        self.departments = config.get("department_names", self.DEFAULT_DEPARTMENTS)
        self.create_service_accounts = config.get("create_service_accounts", True)
        self.service_account_count = config.get("service_account_count", 2)
        
        # Track generated data for relationships
        self.generated_users: list[dict] = []
        self.generated_groups: list[dict] = []
        self.generated_ous: list[dict] = []
    
    def _domain_to_dc_path(self, domain: str) -> str:
        """Convert domain.local to DC=domain,DC=local"""
        parts = domain.split(".")
        return ",".join([f"DC={p}" for p in parts])
    
    def _generate_password(self) -> str:
        """Generate a password based on style."""
        if self.password_style == "weak":
            return random.choice(self.WEAK_PASSWORDS)
        elif self.password_style == "realistic":
            # Realistic but still crackable passwords
            base_words = ["Summer", "Winter", "Spring", "Fall", "Company", "Welcome", "Password"]
            year = random.choice(["2023", "2024", "2025", "!!", "123", "@1"])
            return random.choice(base_words) + year
        else:
            # Strong random
            chars = string.ascii_letters + string.digits + "!@#$%"
            return ''.join(random.choices(chars, k=16))
    
    def _generate_username(self, firstname: str, lastname: str) -> str:
        """Generate username in firstname.lastname format."""
        return f"{firstname.lower()}.{lastname.lower()}"
    
    def generate_ous(self) -> list[dict]:
        """Generate organizational units."""
        ous = []
        # Use departments as OUs, limited to ou_count
        selected_depts = self.departments[:self.ou_count]
        
        for dept in selected_depts:
            ous.append({
                "name": dept,
                "path": self.dc_path
            })
        
        self.generated_ous = ous
        return ous
    
    def generate_groups(self) -> dict[str, list[dict]]:
        """Generate security groups."""
        groups = {
            "global": [],
            "domainlocal": [],
            "universal": []
        }
        
        # Create department groups (global)
        for ou in self.generated_ous:
            groups["global"].append({
                "name": ou["name"],
                "path": f"OU={ou['name']},{self.dc_path}"
            })
        
        # Add some extra groups
        extra_global = ["Managers", "Staff", "Contractors"]
        for i, name in enumerate(extra_global):
            if len(groups["global"]) < self.group_count:
                groups["global"].append({
                    "name": name,
                    "path": f"CN=Users,{self.dc_path}"
                })
        
        # Add a domain local group
        groups["domainlocal"].append({
            "name": "LocalAdmins",
            "path": f"CN=Users,{self.dc_path}"
        })
        
        self.generated_groups = groups
        return groups
    
    def generate_users(self) -> list[dict]:
        """Generate AD users."""
        users = []
        used_usernames = set()
        
        for i in range(self.user_count):
            firstname = self.fake.first_name()
            lastname = self.fake.last_name()
            
            # Ensure unique username
            username = self._generate_username(firstname, lastname)
            counter = 1
            while username in used_usernames:
                username = f"{firstname.lower()}.{lastname.lower()}{counter}"
                counter += 1
            used_usernames.add(username)
            
            # Assign to a random OU/department
            if self.generated_ous:
                ou = random.choice(self.generated_ous)
                path = f"OU={ou['name']},{self.dc_path}"
                dept_group = ou["name"]
            else:
                path = f"CN=Users,{self.dc_path}"
                dept_group = None
            
            # Build group list
            groups = []
            if dept_group and any(g["name"] == dept_group for g in self.generated_groups.get("global", [])):
                groups.append(dept_group)
            
            # Some users are managers
            if random.random() < 0.1:  # 10% are managers
                groups.append("Managers")
            
            user = {
                "name": username,
                "firstname": firstname,
                "surname": lastname,
                "password": self._generate_password(),
                "description": f"{firstname} {lastname}",
                "city": self.fake.city() if self.use_faker else self.fake.city(),
                "path": path,
                "groups": groups,
                "password_never_expires": True
            }
            
            users.append(user)
        
        # Add service accounts if enabled
        if self.create_service_accounts:
            for i in range(self.service_account_count):
                svc_name = f"svc_app{i+1}"
                users.append({
                    "name": svc_name,
                    "firstname": "Service",
                    "surname": f"Account{i+1}",
                    "password": self._generate_password(),
                    "description": f"Service account for application {i+1}",
                    "city": "",
                    "path": f"CN=Users,{self.dc_path}",
                    "groups": [],
                    "spns": [
                        f"HTTP/app{i+1}.{self.domain}",
                        f"HTTP/app{i+1}"
                    ],
                    "password_never_expires": True
                })
        
        self.generated_users = users
        return users
    
    def generate_password_policy(self) -> dict:
        """Generate password policy based on style."""
        if self.password_style == "weak":
            return {
                "min_password_length": 5,
                "password_complexity": False,
                "lockout_threshold": 5,
                "lockout_duration": "00:05:00",
                "lockout_observation": "00:05:00"
            }
        else:
            return {
                "min_password_length": 8,
                "password_complexity": True,
                "lockout_threshold": 5,
                "lockout_duration": "00:30:00",
                "lockout_observation": "00:30:00"
            }
    
    def generate(self) -> dict:
        """Generate complete AD content."""
        # Generate in order (OUs first, then groups, then users)
        ous = self.generate_ous()
        groups = self.generate_groups()
        users = self.generate_users()
        password_policy = self.generate_password_policy()
        
        return {
            "password_policy": password_policy,
            "organisation_units": ous,
            "groups": groups,
            "users": users,
            "multi_domain_group_members": [],
            "_meta": {
                "generator": "ludus_bulk_ad_content",
                "faker_used": self.use_faker,
                "user_count": len(users),
                "group_count": sum(len(v) for v in groups.values()),
                "ou_count": len(ous)
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Generate random AD content")
    parser.add_argument("--config", type=str, required=True, help="JSON config string")
    parser.add_argument("--domain", type=str, required=True, help="Domain FQDN")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        if FAKER_AVAILABLE:
            Faker.seed(args.seed)
    
    # Parse config
    try:
        config = json.loads(args.config)
    except json.JSONDecodeError as e:
        print(f"Error parsing config JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate content
    generator = ADContentGenerator(args.domain, config)
    content = generator.generate()
    
    # Output JSON
    print(json.dumps(content, indent=2))


if __name__ == "__main__":
    main()
