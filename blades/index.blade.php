@extends('../../layouts/back')

@section('content')
    <div class="container mt-4">
        
        @if (session()->has('success'))
            <ul class="alert alert-success ps-5">
                <li>{{ session('success') }}</li>
            </ul>
        @endif

        @if (session()->has('fail'))
            <ul class="alert alert-danger ps-5">
                <li>{{ session('fail') }}</li>
            </ul>
        @endif

        <table class="table table-info">
            <thead>
                <tr>
    
                    <th scope="col">Id</th>
                    <th>created_at</th>
                    <th>updated_at</th>
                    <th>Edit</th>
                    <th>Delete</th>
    
                </tr>
            </thead>
            <tbody>
    
                @foreach ($all as $item)
                    <tr>
                        <td>{{ $item->id }}</td>
                        {{-- toReplace --}}
                        <td>{{ $item->created_at }}</td>
                        <td>{{ $item->updated_at }}</td>
                        <td>
                            <a href="{{ route("modelLower.edit", $item) }}" class="btn btn-primary">EDIT</a>
                        </td>
                        <td>
                            <form action="{{ route("modelLower.destroy", $item) }}" method="post">
                                @csrf
                                @method('DELETE')
                                <input hidden type="text" name="_idvf" value="{{ encrypt($modelLower->id) }}">
                                <button class="btn btn-danger">DELETE</button>
                            </form>
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>
        <a href="{{ route("modelLower.create") }}" class="btn btn-success">CREATE</a>
    </div>
@endsection